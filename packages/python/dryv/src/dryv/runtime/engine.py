from __future__ import annotations

import base64
import json
import threading
from dataclasses import dataclass
from typing import Iterable, Sequence, cast

from dryv.features.artifacts import (
    ArtifactFeature,
    ArtifactProvenance,
    GeneratedArtifact,
)
from dryv.features.authoring import AUTHOR_PROTOCOL_VERSION, AuthoringFeature
from dryv.features.cache import (
    CacheEntry,
    CacheFeature,
    CacheStage,
    CacheTransaction,
    ContextCacheKey,
    RenderCacheKey,
)
from dryv.features.hashing import (
    HashPurpose,
    canonical_bytes,
    hash_branch,
    hash_bytes,
    hash_value,
)
from dryv.features.ir import IRFeature, IRSnapshot
from dryv.features.packs import NormalizedPack, decode_pack_manifest, normalize_pack
from dryv.features.planning import (
    GenerationPlan,
    InvocationStatus,
    PlanningFeature,
)
from dryv.features.project import decode_project
from dryv.features.resources import ResourceRegistry
from dryv.features.scheduling import (
    JobStatus,
    ScheduledJob,
    SchedulingFeature,
    WorkerCapacity,
    WorkSession,
)
from dryv.features.serialization import (
    RepresentationRecord,
    canonical_record_bytes,
    contract_from_json,
    contract_from_jsonl,
    contract_from_records,
    contract_from_yaml,
    contract_to_records,
)
from dryv.features.templating import (
    RENDER_PROTOCOL_VERSION,
    PlannedOutput,
    RenderRequest,
    RenderedOutput,
    TemplatingFeature,
)
from dryv.ir import Contract
from dryv.versions import CORE_VERSION

from .contracts import (
    AvailableRenderSession,
    BuildCacheStats,
    BuildDiagnostic,
    BuildRequest,
    BuildResult,
    BuildStatus,
    BuildTrace,
    RuntimeBuildError,
    RuntimeSnapshot,
)

_FEATURE_NAMES = (
    "serialization",
    "project",
    "resources",
    "hashing",
    "ir",
    "packs",
    "planning",
    "cache",
    "authoring",
    "templating",
    "scheduling",
    "artifacts",
    "diagnostics",
)


@dataclass(frozen=True, slots=True)
class _NormalizedPackInput:
    pack: NormalizedPack
    manifest_hash: str


@dataclass(frozen=True, slots=True)
class _RenderWorkResult:
    invocation_id: str
    worker_id: str
    outputs: tuple[RenderedOutput, ...]
    cache_hit: bool


class _RenderWorker(WorkSession):
    def __init__(
        self,
        available: AvailableRenderSession,
        *,
        templating: TemplatingFeature,
        cache: CacheTransaction,
        cache_lock: threading.Lock,
    ) -> None:
        self._id = available.session_id
        self._session = available.session
        self._hello = available.session.hello()
        self._templating = templating
        self._cache = cache
        self._cache_lock = cache_lock

    def capacity(self) -> WorkerCapacity:
        return WorkerCapacity(
            self._id,
            self._hello.capabilities,
            self._hello.max_concurrency,
        )

    def execute(self, job: ScheduledJob) -> object:
        request = cast(RenderRequest, job.payload)
        fingerprint_hash = hash_value(
            HashPurpose.RENDERER_FINGERPRINT,
            {
                "fingerprint": self._hello.fingerprint,
                "rendererId": self._hello.renderer_id,
                "rendererVersion": self._hello.renderer_version,
            },
        ).identity
        options_hash = hash_value(
            HashPurpose.BUILD_INPUT,
            {"options": [[name, value] for name, value in request.options]},
        ).identity
        key = RenderCacheKey(
            context_hash=request.context_hash,
            template_hash=request.template_hash,
            renderer_fingerprint_hash=fingerprint_hash,
            render_options_hash=options_hash,
            render_protocol_version=request.protocol_version,
            context_version=request.context_version,
        )
        with self._cache_lock:
            cached = self._cache.get(CacheStage.RENDER, key)
        if cached is not None:
            return _RenderWorkResult(
                invocation_id=request.job_id,
                worker_id=self._id,
                outputs=_decode_render_outputs(cached.payload),
                cache_hit=True,
            )

        rendered = self._templating.render(
            self._session,
            request,
            content_hash=lambda content: hash_bytes(
                HashPurpose.ARTIFACT_CONTENT, content
            ).identity,
        )
        payload = _encode_render_outputs(rendered.outputs)
        with self._cache_lock:
            self._cache.put(
                CacheEntry(
                    CacheStage.RENDER,
                    key,
                    payload,
                    metadata=(
                        ("rendererFingerprint", self._hello.fingerprint),
                        ("sessionId", self._id),
                    ),
                )
            )
        return _RenderWorkResult(
            invocation_id=request.job_id,
            worker_id=self._id,
            outputs=rendered.outputs,
            cache_hit=False,
        )

    def cancel(self, job_id: str) -> None:
        self._session.cancel(job_id)


class DryvRuntime:
    """Transport-neutral composition root for the Dryv Engine."""

    def __init__(
        self,
        *,
        cache: CacheFeature | None = None,
        ir: IRFeature | None = None,
        planning: PlanningFeature | None = None,
        authoring: AuthoringFeature | None = None,
        templating: TemplatingFeature | None = None,
        scheduling: SchedulingFeature | None = None,
        artifacts: ArtifactFeature | None = None,
    ) -> None:
        self.cache = cache or CacheFeature()
        self.ir = ir or IRFeature()
        self.planning = planning or PlanningFeature()
        self.authoring = authoring or AuthoringFeature()
        self.templating = templating or TemplatingFeature()
        self.scheduling = scheduling or SchedulingFeature()
        self.artifacts = artifacts or ArtifactFeature()

    def snapshot(self) -> RuntimeSnapshot:
        return RuntimeSnapshot(
            core_version=str(CORE_VERSION),
            features=_FEATURE_NAMES,
            author_protocol_version=AUTHOR_PROTOCOL_VERSION,
            render_protocol_version=RENDER_PROTOCOL_VERSION,
        )

    def build(self, request: BuildRequest) -> BuildResult:
        trace: list[BuildTrace] = []
        transaction = self.cache.begin(
            request.cache_mode,
            commit_enabled=request.commit_cache,
        )
        try:
            registry = self._resources(request, trace)
            self._project(request, trace)
            contract = self._contract(request, registry, trace)
            snapshot = self.ir.load_contract(contract)
            if not snapshot.valid:
                transaction.rollback()
                return BuildResult(
                    request.build_id,
                    BuildStatus.FAILED,
                    False,
                    None,
                    None,
                    tuple(trace),
                    tuple(
                        BuildDiagnostic(item.code, item.message)
                        for item in snapshot.diagnostics.errors
                    ),
                )
            trace.append(
                BuildTrace(
                    "ir",
                    str(contract.id),
                    "Canonical IR validated and indexed",
                    (("records", str(len(snapshot.objects))),),
                )
            )

            packs = self._packs(request, registry, trace)
            self._validate_candidates(request, packs)
            plan = self.planning.build(request.planning_candidates)
            trace.extend(_plan_trace(plan))

            context_stats = self._context_cache(
                transaction,
                plan,
                snapshot,
                packs,
                request,
                trace,
            )
            cache_lock = threading.Lock()
            workers = tuple(
                _RenderWorker(
                    available,
                    templating=self.templating,
                    cache=transaction,
                    cache_lock=cache_lock,
                )
                for available in sorted(
                    request.render_sessions,
                    key=lambda item: item.session_id,
                )
            )
            schedule_jobs = self._render_jobs(plan, registry)
            report = self.scheduling.run(
                schedule_jobs,
                workers,
                cancellation=request.cancellation,
                on_dispatch=lambda job, worker, attempt: trace.append(
                    BuildTrace(
                        "render-dispatch",
                        job.id,
                        "render job dispatched",
                        (
                            ("attempt", str(attempt)),
                            ("session", worker.worker_id),
                        ),
                    )
                ),
            )
            if not report.success:
                transaction.rollback()
                cancelled = any(
                    item.status is JobStatus.CANCELLED for item in report.results
                )
                diagnostics = tuple(
                    BuildDiagnostic(
                        f"RUNTIME_RENDER_{item.status.value.upper()}",
                        item.error or f"render job {item.job_id} did not succeed",
                        item.job_id,
                    )
                    for item in report.results
                    if item.status is not JobStatus.SUCCEEDED
                )
                return BuildResult(
                    request.build_id,
                    BuildStatus.CANCELLED if cancelled else BuildStatus.FAILED,
                    False,
                    plan,
                    None,
                    tuple(trace),
                    diagnostics,
                    BuildCacheStats(
                        context_hits=context_stats[0],
                        context_misses=context_stats[1],
                    ),
                )

            render_results = {
                result.job_id: cast(_RenderWorkResult, result.value)
                for result in report.results
            }
            generated = self._generated_artifacts(plan, render_results, trace)
            classification = self.artifacts.classify(
                generated,
                previous=request.previous_managed_outputs,
                snapshot=request.project_snapshot,
            )
            for instruction in classification.instructions:
                trace.append(
                    BuildTrace(
                        "artifact",
                        instruction.path,
                        instruction.reason,
                        (("writeKind", instruction.kind.value),),
                    )
                )

            transaction.commit()
            render_hits = sum(1 for item in render_results.values() if item.cache_hit)
            render_misses = len(render_results) - render_hits
            return BuildResult(
                request.build_id,
                BuildStatus.RENDER_COMPLETE,
                True,
                plan,
                classification,
                tuple(trace),
                (),
                BuildCacheStats(
                    context_hits=context_stats[0],
                    context_misses=context_stats[1],
                    render_hits=render_hits,
                    render_misses=render_misses,
                ),
            )
        except Exception as exc:  # noqa: BLE001 - Feature errors are normalized at Runtime boundary
            try:
                transaction.rollback()
            except RuntimeError:
                pass
            code = getattr(exc, "code", "RUNTIME_BUILD_ERROR")
            subject = getattr(exc, "subject", None) or getattr(exc, "path", None)
            return BuildResult(
                request.build_id,
                BuildStatus.CANCELLED
                if request.cancellation is not None and request.cancellation.cancelled
                else BuildStatus.FAILED,
                False,
                None,
                None,
                tuple(trace),
                (BuildDiagnostic(str(code), str(exc), subject),),
            )

    @staticmethod
    def _resources(request: BuildRequest, trace: list[BuildTrace]) -> ResourceRegistry:
        registry = ResourceRegistry()
        for item in sorted(request.resources, key=lambda value: value.resource_id):
            resource = registry.register_bytes(
                item.resource_id,
                item.media_type,
                item.content,
                content_hash=item.content_hash,
            )
            trace.append(
                BuildTrace(
                    "resource",
                    str(resource.descriptor.id),
                    "logical resource registered",
                    (("hash", str(resource.descriptor.content_hash)),),
                )
            )
        return registry

    @staticmethod
    def _project(request: BuildRequest, trace: list[BuildTrace]) -> None:
        if request.project_document is None:
            return
        project = decode_project(dict(request.project_document))
        trace.append(
            BuildTrace(
                "project",
                project.name,
                "dryv.yaml meaning normalized",
                (("packs", str(len(project.packs))),),
            )
        )

    def _contract(
        self,
        request: BuildRequest,
        registry: ResourceRegistry,
        trace: list[BuildTrace],
    ) -> Contract:
        if request.precompiled_contract is not None:
            trace.append(
                BuildTrace(
                    "authoring",
                    str(request.precompiled_contract.id),
                    "precompiled Canonical IR supplied; Author Session bypassed",
                )
            )
            return request.precompiled_contract

        if request.precompiled_ir_resource_id is not None:
            resource = registry.require(request.precompiled_ir_resource_id)
            contract = _decode_contract_resource(
                resource.descriptor.media_type,
                resource.content,
            )
            trace.append(
                BuildTrace(
                    "serialization",
                    request.precompiled_ir_resource_id,
                    "precompiled Canonical IR resource decoded",
                )
            )
            return contract

        assert request.author is not None
        result = self.authoring.resolve(
            precompiled=None,
            validator=lambda value: self.ir.load_contract(value).diagnostics,
            session=request.author.session,
            request=request.author.request,
            decode_document=_decode_contract_resource,
            decode_records=_decode_author_records,
            is_cancelled=(
                (lambda: request.cancellation.cancelled)
                if request.cancellation is not None
                else None
            ),
        )
        trace.append(
            BuildTrace(
                "authoring",
                request.author.request.job_id,
                "Author Session produced validated Canonical IR",
                (("backend", result.hello.backend_id if result.hello else "precompiled"),),
            )
        )
        return result.contract

    @staticmethod
    def _packs(
        request: BuildRequest,
        registry: ResourceRegistry,
        trace: list[BuildTrace],
    ) -> dict[str, _NormalizedPackInput]:
        normalized: dict[str, _NormalizedPackInput] = {}
        for item in request.packs:
            manifest = decode_pack_manifest(dict(item.manifest_document))
            pack = normalize_pack(
                manifest,
                item.templates,
                manifest_resource_id=item.manifest_resource_id,
            )
            if manifest.id in normalized:
                raise RuntimeBuildError(
                    "RUNTIME_DUPLICATE_PACK",
                    f"duplicate pack id {manifest.id!r}",
                    subject=manifest.id,
                )
            for template in pack.templates:
                registry.require(template.resource_id)
            manifest_hash = hash_value(
                HashPurpose.PACK_MANIFEST,
                cast(dict[str, object], dict(item.manifest_document)),
            ).identity
            normalized[manifest.id] = _NormalizedPackInput(pack, manifest_hash)
            trace.append(
                BuildTrace(
                    "pack",
                    manifest.id,
                    "pack manifest normalized",
                    (("templates", str(len(pack.templates))),),
                )
            )
        return normalized

    @staticmethod
    def _validate_candidates(
        request: BuildRequest,
        packs: dict[str, _NormalizedPackInput],
    ) -> None:
        for candidate in request.planning_candidates:
            pack_input = packs.get(candidate.pack_id)
            if pack_input is None:
                raise RuntimeBuildError(
                    "RUNTIME_PLAN_PACK",
                    f"planning candidate references unknown pack {candidate.pack_id!r}",
                    subject=candidate.invocation_id,
                )
            template = next(
                (
                    item
                    for item in pack_input.pack.templates
                    if item.resource_id == candidate.template_resource_id
                ),
                None,
            )
            if template is None:
                raise RuntimeBuildError(
                    "RUNTIME_PLAN_TEMPLATE",
                    f"planning candidate references unknown template resource {candidate.template_resource_id!r}",
                    subject=candidate.invocation_id,
                )
            if (
                template.selection_key is not None
                and template.selection_key != candidate.selection_key
            ):
                raise RuntimeBuildError(
                    "RUNTIME_PLAN_SELECTION",
                    "planning candidate selection does not match the pack template declaration",
                    subject=candidate.invocation_id,
                )

    @staticmethod
    def _context_cache(
        transaction: CacheTransaction,
        plan: GenerationPlan,
        snapshot: IRSnapshot,
        packs: dict[str, _NormalizedPackInput],
        request: BuildRequest,
        trace: list[BuildTrace],
    ) -> tuple[int, int]:
        direct_hashes = {
            record.id: hash_bytes(HashPurpose.IR_RECORD, canonical_record_bytes(record))
            for record in contract_to_records(snapshot.contract)
        }
        dependencies = {
            str(identity): tuple(str(item) for item in values if str(item) in direct_hashes)
            for identity, values in snapshot.dependencies.items()
            if str(identity) in direct_hashes
        }
        hits = 0
        misses = 0
        for invocation in plan.invocations:
            if invocation.status is not InvocationStatus.PLANNED or invocation.context is None:
                continue
            dependency_hashes: list[tuple[str, str]] = []
            for dependency in invocation.semantic_dependencies:
                if dependency not in direct_hashes:
                    raise RuntimeBuildError(
                        "RUNTIME_CONTEXT_DEPENDENCY",
                        f"planned context references unknown semantic dependency {dependency!r}",
                        subject=invocation.id,
                    )
                dependency_hashes.append(
                    (
                        dependency,
                        hash_branch(dependency, direct_hashes, dependencies).identity,
                    )
                )
            pack_hash = packs[invocation.pack_id].manifest_hash
            inputs_hash = hash_value(
                HashPurpose.BUILD_INPUT,
                {
                    "bindingsUsed": list(invocation.bindings_used),
                    "optionsUsed": list(invocation.options_used),
                },
            ).identity
            key = ContextCacheKey(
                tuple(sorted(dependency_hashes)),
                plan.context_version,
                pack_hash,
                inputs_hash,
            )
            cached = transaction.get(CacheStage.CONTEXT, key)
            if cached is not None:
                hits += 1
                state = "hit"
            else:
                misses += 1
                state = "miss"
                transaction.put(
                    CacheEntry(
                        CacheStage.CONTEXT,
                        key,
                        canonical_bytes(cast(object, invocation.context)),
                        metadata=(("invocation", invocation.id),),
                    )
                )
            trace.append(
                BuildTrace(
                    "context-cache",
                    invocation.id,
                    f"context cache {state}",
                    (("mode", request.cache_mode.value),),
                )
            )
        return hits, misses

    @staticmethod
    def _render_jobs(
        plan: GenerationPlan,
        registry: ResourceRegistry,
    ) -> tuple[ScheduledJob, ...]:
        artifact_to_invocation = {
            artifact.id: artifact.invocation_id for artifact in plan.artifacts
        }
        jobs: list[ScheduledJob] = []
        order_by_artifact = {artifact.id: index for index, artifact in enumerate(plan.artifacts)}
        for invocation in plan.invocations:
            if invocation.status is not InvocationStatus.PLANNED:
                continue
            if invocation.context is None or invocation.artifact_id is None:
                raise RuntimeBuildError(
                    "RUNTIME_PLAN_INCOMPLETE",
                    "planned render invocation is missing context or artifact identity",
                    subject=invocation.id,
                )
            artifact = plan.artifact(invocation.artifact_id)
            if artifact is None:
                raise RuntimeBuildError(
                    "RUNTIME_PLAN_ARTIFACT",
                    "planned invocation references a missing virtual artifact",
                    subject=invocation.id,
                )
            template = registry.require(invocation.template_resource_id)
            template_hash = hash_bytes(
                HashPurpose.TEMPLATE_CONTENT,
                template.content,
            ).identity
            context_hash = hash_value(
                HashPurpose.CONTEXT,
                cast(object, invocation.context),
            ).identity
            render_request = RenderRequest(
                protocol_version=RENDER_PROTOCOL_VERSION,
                context_version=plan.context_version,
                job_id=invocation.id,
                required_capability=invocation.renderer_capability,
                template_resource_id=invocation.template_resource_id,
                template_media_type=template.descriptor.media_type,
                template_content=template.content,
                template_hash=template_hash,
                context=cast(dict[str, object], invocation.context),
                context_hash=context_hash,
                outputs=(PlannedOutput(artifact.id, artifact.path),),
            )
            dependencies = tuple(
                artifact_to_invocation[item]
                for item in artifact.dependencies
                if item in artifact_to_invocation
            )
            jobs.append(
                ScheduledJob(
                    id=invocation.id,
                    required_capability=invocation.renderer_capability,
                    dependencies=dependencies,
                    order=order_by_artifact[artifact.id],
                    payload=render_request,
                )
            )
        return tuple(jobs)

    @staticmethod
    def _generated_artifacts(
        plan: GenerationPlan,
        render_results: dict[str, _RenderWorkResult],
        trace: list[BuildTrace],
    ) -> tuple[GeneratedArtifact, ...]:
        generated: list[GeneratedArtifact] = []
        for invocation in plan.invocations:
            if invocation.status is not InvocationStatus.PLANNED:
                continue
            result = render_results[invocation.id]
            if len(result.outputs) != 1:
                raise RuntimeBuildError(
                    "RUNTIME_OUTPUT_CARDINALITY",
                    "runtime planning currently expects one logical output per planned invocation",
                    subject=invocation.id,
                )
            output = result.outputs[0]
            artifact = plan.artifact(output.id)
            if artifact is None or invocation.artifact_id != output.id:
                raise RuntimeBuildError(
                    "RUNTIME_OUTPUT_PLAN",
                    "validated render output is not the invocation's planned artifact",
                    subject=invocation.id,
                )
            generated.append(
                GeneratedArtifact(
                    artifact_id=artifact.id,
                    path=artifact.path,
                    logical_output_id=output.id,
                    content=output.content,
                    content_hash=output.content_hash,
                    ownership_id=f"{invocation.pack_id}:{invocation.selection_key}",
                    provenance=ArtifactProvenance(
                        semantic_ids=invocation.semantic_ids,
                        pack_id=invocation.pack_id,
                        selection_key=invocation.selection_key,
                        template_resource_id=invocation.template_resource_id,
                        invocation_id=invocation.id,
                    ),
                    dependencies=artifact.dependencies,
                )
            )
            trace.append(
                BuildTrace(
                    "render-result",
                    invocation.id,
                    "validated render result accepted",
                    (
                        ("artifact", artifact.id),
                        ("cache", "hit" if result.cache_hit else "miss"),
                        ("session", result.worker_id),
                    ),
                )
            )
        return tuple(generated)


def _decode_contract_resource(media_type: str, content: bytes) -> Contract:
    normalized = media_type.split(";", 1)[0].strip().lower()
    if normalized in {"application/json", "application/vnd.dryv.ir+json"}:
        return contract_from_json(content)
    if normalized in {
        "application/yaml",
        "application/x-yaml",
        "text/yaml",
        "application/vnd.dryv.ir+yaml",
    }:
        return contract_from_yaml(content)
    if normalized in {
        "application/jsonl",
        "application/x-ndjson",
        "application/vnd.dryv.ir+jsonl",
    }:
        return contract_from_jsonl((content,))
    raise RuntimeBuildError(
        "RUNTIME_IR_MEDIA_TYPE",
        f"unsupported Canonical IR media type {media_type!r}",
    )


def _decode_author_records(records: Iterable[object]) -> Contract:
    typed: list[RepresentationRecord] = []
    for record in records:
        if not isinstance(record, RepresentationRecord):
            raise RuntimeBuildError(
                "RUNTIME_AUTHOR_RECORD",
                "Author Session record stream must contain canonical RepresentationRecord values",
            )
        typed.append(record)
    return contract_from_records(typed)


def _plan_trace(plan: GenerationPlan) -> tuple[BuildTrace, ...]:
    trace: list[BuildTrace] = []
    for invocation in plan.invocations:
        trace.append(
            BuildTrace(
                "planning",
                invocation.id,
                (
                    invocation.skip_reason
                    if invocation.status is InvocationStatus.SKIPPED
                    else "template invocation planned"
                ),
                (
                    ("pack", invocation.pack_id),
                    ("selection", invocation.selection_key),
                    ("template", invocation.template_resource_id),
                ),
            )
        )
    return tuple(trace)


def _encode_render_outputs(outputs: Sequence[RenderedOutput]) -> bytes:
    document = {
        "outputs": [
            {
                "content": base64.b64encode(item.content).decode("ascii"),
                "contentHash": item.content_hash,
                "id": item.id,
            }
            for item in sorted(outputs, key=lambda value: value.id)
        ]
    }
    return json.dumps(document, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _decode_render_outputs(payload: bytes) -> tuple[RenderedOutput, ...]:
    try:
        document = json.loads(payload.decode("utf-8"))
        raw = document["outputs"]
        if not isinstance(raw, list):
            raise TypeError
        outputs = tuple(
            RenderedOutput(
                str(item["id"]),
                base64.b64decode(str(item["content"]), validate=True),
                str(item["contentHash"]),
            )
            for item in raw
            if isinstance(item, dict)
        )
    except (KeyError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeBuildError(
            "RUNTIME_RENDER_CACHE",
            "render cache payload is invalid",
        ) from exc
    if len(outputs) != len(raw):
        raise RuntimeBuildError("RUNTIME_RENDER_CACHE", "render cache output record is invalid")
    return tuple(sorted(outputs, key=lambda item: item.id))


__all__ = ["DryvRuntime"]
