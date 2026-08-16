from __future__ import annotations

from collections.abc import Callable

from dryv.features.cache import CacheFeature
from dryv.features.diagnostics import DiagnosticsFeature
from dryv.features.hashing import HashPurpose, hash_bytes, hash_value
from dryv.features.ir import IRFeature, IRSnapshot
from dryv.features.packs import SelectionKind, load_pack_manifest, resolve_pack
from dryv.features.planning import (
    PlanningFeature,
    PlanningInput,
    PlanningName,
    PlanningPack,
    PlanningSelection,
    PlanningSubject,
    PlanningTemplate,
)
from dryv.features.project import ProjectConfig, load_project, thaw_object
from dryv.features.resources import ResourceRegistry
from dryv.features.serialization import contract_to_document, decode_contract, encode_value
from dryv.ir import Name, SemanticId
from dryv.versions import CORE_VERSION

from .contracts import (
    RuntimeDiagnostic,
    RuntimeInput,
    RuntimePack,
    RuntimeResult,
    RuntimeSnapshot,
    RuntimeStatus,
    RuntimeTrace,
)
from .events import RuntimeEvent, RuntimeEventSink, RuntimeStage

_FEATURES = (
    "serialization",
    "project",
    "resources",
    "hashing",
    "ir",
    "packs",
    "planning",
    "cache",
    "diagnostics",
)
_SELECTABLE_KINDS = {item.value for item in SelectionKind}


class DryvRuntime:
    """Composition root that turns explicit Dryv build inputs into one GenerationPlan."""

    def __init__(
        self,
        *,
        ir: IRFeature | None = None,
        planning: PlanningFeature | None = None,
        cache: CacheFeature | None = None,
        diagnostics: DiagnosticsFeature | None = None,
    ) -> None:
        self.ir = ir or IRFeature()
        self.planning = planning or PlanningFeature()
        self.cache = cache or CacheFeature()
        self.diagnostics = diagnostics or DiagnosticsFeature()

    def snapshot(self) -> RuntimeSnapshot:
        return RuntimeSnapshot(str(CORE_VERSION), _FEATURES)

    def plan(self, request: RuntimeInput, *, events: RuntimeEventSink | None = None) -> RuntimeResult:
        trace: list[RuntimeTrace] = []
        self._record(request.build_id, RuntimeStage.STARTED, "Dryv Runtime planning started", trace, events)
        try:
            registry = self._resources(request)
            project = self._project(request, registry, trace, events)
            snapshot, ir_hash = self._ir(request, registry, trace, events)
            if not snapshot.valid:
                diagnostics = tuple(_ir_diagnostic(item) for item in snapshot.diagnostics.items)
                self._record(request.build_id, RuntimeStage.FAILED, "Canonical IR validation failed", trace, events)
                return RuntimeResult(request.build_id, RuntimeStatus.FAILED, None, diagnostics, tuple(trace))
            packs = self._packs(request, project, registry, trace, events)
            planning_input = PlanningInput(
                request.build_id,
                project.name,
                ir_hash,
                self._subjects(snapshot),
                packs,
            )
            self._record(request.build_id, RuntimeStage.PLANNING, "Generation planning started", trace, events)
            plan = self.planning.build(
                planning_input,
                hash_context=lambda value: hash_value(HashPurpose.CONTEXT, value).identity,
                hash_context_contract=lambda value: hash_value(HashPurpose.CONTEXT_CONTRACT, value).identity,
                hash_plan=lambda value: hash_value(HashPurpose.GENERATION_PLAN, value).identity,
            )
            self._record(
                request.build_id,
                RuntimeStage.COMPLETE,
                "GenerationPlan complete",
                trace,
                events,
                details=(("jobs", str(len(plan.jobs))), ("artifacts", str(len(plan.artifacts)))),
            )
            return RuntimeResult(request.build_id, RuntimeStatus.PLAN_COMPLETE, plan, (), tuple(trace))
        except Exception as exc:
            entry = self.diagnostics.from_error(exc)
            diagnostic = RuntimeDiagnostic(entry.code, entry.message, entry.level.value, entry.subject, entry.details)
            self._record(request.build_id, RuntimeStage.FAILED, entry.message, trace, events, subject=entry.subject)
            return RuntimeResult(request.build_id, RuntimeStatus.FAILED, None, (diagnostic,), tuple(trace))

    def _resources(self, request: RuntimeInput) -> ResourceRegistry:
        registry = ResourceRegistry()
        for item in request.resources:
            registry.register_bytes(item.resource_id, item.media_type, item.content, content_hash=item.content_hash)
        return registry

    def _project(
        self,
        request: RuntimeInput,
        registry: ResourceRegistry,
        trace: list[RuntimeTrace],
        events: RuntimeEventSink | None,
    ) -> ProjectConfig:
        resource = registry.require(request.project_resource_id)
        project = load_project(resource.content, resource.descriptor.media_type)
        expected = {item.name for item in project.packs}
        supplied = {item.instance_name for item in request.packs}
        if expected != supplied:
            missing = sorted(expected - supplied)
            extra = sorted(supplied - expected)
            raise ValueError(f"resolved pack bundles do not match dryv.yaml; missing={missing}, extra={extra}")
        for resource_id in project.resources:
            registry.require(resource_id)
        self._record(request.build_id, RuntimeStage.PROJECT, "dryv.yaml validated", trace, events, subject=project.name)
        return project

    def _ir(
        self,
        request: RuntimeInput,
        registry: ResourceRegistry,
        trace: list[RuntimeTrace],
        events: RuntimeEventSink | None,
    ) -> tuple[IRSnapshot, str]:
        resource = registry.require(request.canonical_ir_resource_id)
        contract = decode_contract(resource.content, resource.descriptor.media_type)
        snapshot = self.ir.load(contract)
        digest = hash_value(HashPurpose.CANONICAL_DOCUMENT, contract_to_document(contract)).identity
        self._record(
            request.build_id,
            RuntimeStage.IR,
            "Canonical IR loaded and validated",
            trace,
            events,
            subject=str(contract.id),
            details=(("objects", str(len(snapshot.objects))),),
        )
        return snapshot, digest

    def _packs(
        self,
        request: RuntimeInput,
        project: ProjectConfig,
        registry: ResourceRegistry,
        trace: list[RuntimeTrace],
        events: RuntimeEventSink | None,
    ) -> tuple[PlanningPack, ...]:
        supplied = {item.instance_name: item for item in request.packs}
        result: list[PlanningPack] = []
        for config in project.packs:
            bundle = supplied[config.name]
            manifest_resource = registry.require(bundle.manifest_resource_id)
            manifest = load_pack_manifest(manifest_resource.content, manifest_resource.descriptor.media_type)
            manifest_hash = hash_bytes(HashPurpose.PACK_MANIFEST, manifest_resource.content).identity
            resolved = resolve_pack(
                manifest,
                options=config.options,
                bindings=config.bindings,
                manifest_resource_id=bundle.manifest_resource_id,
                manifest_hash=manifest_hash,
            )
            resource_map = {item.relative_path: item.resource_id for item in bundle.resources}
            templates: list[PlanningTemplate] = []
            for template in manifest.templates:
                resource_id = resource_map.get(template.file)
                if resource_id is None:
                    raise ValueError(f"pack {config.name!r} is missing template resource {template.file!r}")
                resource = registry.require(resource_id)
                templates.append(
                    PlanningTemplate(
                        template.key,
                        template.selection,
                        resource_id,
                        template.file,
                        resource.descriptor.media_type,
                        resource.descriptor.content_hash,
                        template.renderer,
                        template.output,
                        template.depends_on,
                    )
                )
            result.append(
                PlanningPack(
                    config.name,
                    manifest.id,
                    manifest.version,
                    config.output,
                    resolved.manifest_hash,
                    _frozen_object(resolved.options),
                    _frozen_object(resolved.bindings),
                    tuple(PlanningSelection(item.key, item.kind.value, item.bindings, item.symbols) for item in manifest.selections),
                    tuple(templates),
                )
            )
            self._record(
                request.build_id,
                RuntimeStage.PACKS,
                "Template Pack validated",
                trace,
                events,
                subject=config.name,
                details=(("pack", manifest.id), ("templates", str(len(manifest.templates)))),
            )
        return tuple(result)

    def _subjects(self, snapshot: IRSnapshot) -> tuple[PlanningSubject, ...]:
        result: list[PlanningSubject] = []
        for identity, value in sorted(snapshot.objects.items(), key=lambda item: str(item[0])):
            kind = snapshot.kinds[identity]
            if kind not in _SELECTABLE_KINDS:
                continue
            encoded = encode_value(value)
            if not isinstance(encoded, dict):
                raise ValueError(f"canonical subject {identity} did not encode to an object")
            effective = None
            if kind == "schema":
                effective_value = encode_value(self.ir.effective_schema(snapshot, identity))
                if not isinstance(effective_value, dict):
                    raise ValueError(f"effective schema {identity} did not encode to an object")
                effective = effective_value
            result.append(
                PlanningSubject(
                    str(identity),
                    kind,
                    _planning_name(value, identity),
                    encoded,
                    tuple(str(item) for item in snapshot.dependencies.get(identity, ())),
                    effective,
                )
            )
        return tuple(result)

    def _record(
        self,
        build_id: str,
        stage: RuntimeStage,
        message: str,
        trace: list[RuntimeTrace],
        events: RuntimeEventSink | None,
        *,
        subject: str | None = None,
        details: tuple[tuple[str, str], ...] = (),
    ) -> None:
        trace.append(RuntimeTrace(stage.value, message, subject, details))
        if events is not None:
            events(RuntimeEvent(build_id, stage, message, subject, details))


def _planning_name(value: object, identity: SemanticId) -> PlanningName:
    name = getattr(value, "name", None)
    if isinstance(name, Name):
        return PlanningName(
            name.value,
            name.raw.singular,
            name.raw.plural,
            name.snake.original,
            name.kebab.original,
            name.camel.original,
            name.pascal.original,
        )
    fallback = str(identity).replace("/", " ").replace(":", " ").replace(".", " ").split()[-1]
    generated = Name(fallback)
    return PlanningName(
        generated.value,
        generated.raw.singular,
        generated.raw.plural,
        generated.snake.original,
        generated.kebab.original,
        generated.camel.original,
        generated.pascal.original,
    )


def _frozen_object(value: tuple[tuple[str, object], ...]) -> dict[str, object]:
    return {key: _thaw(item) for key, item in value}


def _thaw(value: object) -> object:
    if not isinstance(value, tuple):
        return value
    if value and all(isinstance(item, tuple) and len(item) == 2 for item in value):
        return {key: _thaw(item) for key, item in value}
    return [_thaw(item) for item in value]


def _ir_diagnostic(value: object) -> RuntimeDiagnostic:
    severity = getattr(getattr(value, "severity", None), "value", "error")
    details = tuple((str(key), str(item)) for key, item in getattr(value, "details", ()))
    span = getattr(value, "span", None)
    subject = None if span is None else str(getattr(getattr(span, "source", None), "identifier", "")) or None
    return RuntimeDiagnostic(str(getattr(value, "code", "IR_ERROR")), str(getattr(value, "message", value)), severity, subject, details)


__all__ = ["DryvRuntime"]
