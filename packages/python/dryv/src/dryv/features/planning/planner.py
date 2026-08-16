from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, replace

from .context import build_context, context_contract
from .contracts import (
    CONTEXT_VERSION,
    PLAN_VERSION,
    GenerationPlan,
    JsonObject,
    JsonValue,
    PlanDependency,
    PlannedArtifact,
    PlanningError,
    PlanningInput,
    PlanningPack,
    PlanningSelection,
    PlanningSubject,
    PlanningTemplate,
    RenderJob,
    RendererRequirement,
    TemplateReference,
)
from .selection import output_path, selected_subjects

_MAX_CONTEXT_BYTES = 2 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class _Draft:
    id: str
    subject: PlanningSubject
    pack: PlanningPack
    selection: PlanningSelection
    template: PlanningTemplate
    artifact: PlannedArtifact


class PlanningFeature:
    def build(
        self,
        value: PlanningInput,
        *,
        hash_context: Callable[[JsonValue], str],
        hash_context_contract: Callable[[JsonValue], str],
        hash_plan: Callable[[JsonValue], str],
    ) -> GenerationPlan:
        subjects = {item.id: item for item in value.subjects}
        if len(subjects) != len(value.subjects):
            raise PlanningError("PLAN_DUPLICATE_SUBJECT", "planning subject ids must be unique")
        drafts = _draft_jobs(value)
        dependencies = _resolve_dependencies(drafts)
        dependency_map: dict[str, tuple[str, ...]] = {
            draft.id: tuple(sorted(item.depends_on_job_id for item in dependencies if item.job_id == draft.id))
            for draft in drafts
        }
        by_job = {item.id: item for item in drafts}
        ordered_ids = _order_jobs(tuple(by_job), dependency_map)
        order = {identity: index for index, identity in enumerate(ordered_ids)}
        jobs: list[RenderJob] = []
        artifacts: list[PlannedArtifact] = []

        for draft in drafts:
            job_dependencies = dependency_map[draft.id]
            dependency_artifacts = tuple(by_job[item].artifact for item in job_dependencies)
            semantic_dependencies = tuple(
                subjects[item]
                for item in draft.subject.semantic_dependencies
                if item in subjects
            )
            artifact = replace(
                draft.artifact,
                dependencies=tuple(item.id for item in dependency_artifacts),
            )
            context = build_context(
                project_name=value.project_name,
                subject=draft.subject,
                semantic_dependencies=semantic_dependencies,
                dependency_artifacts=dependency_artifacts,
                artifact=artifact,
                pack=draft.pack,
                selection=draft.selection,
            )
            _context_size(context, draft.id)
            contract = context_contract(context, hasher=hash_context_contract)
            context_hash = hash_context(context)
            reference = TemplateReference(
                draft.pack.pack_id,
                draft.pack.instance_name,
                draft.template.key,
                draft.template.resource_id,
                draft.template.relative_path,
                draft.template.media_type,
                draft.template.content_hash,
            )
            jobs.append(
                RenderJob(
                    draft.id,
                    order[draft.id],
                    draft.subject.id,
                    draft.subject.kind,
                    draft.pack.pack_id,
                    draft.pack.instance_name,
                    draft.selection.key,
                    f"selection {draft.selection.key!r} matched canonical kind {draft.selection.kind!r}",
                    RendererRequirement(draft.template.renderer),
                    reference,
                    context,
                    contract,
                    context_hash,
                    artifact,
                    job_dependencies,
                    draft.subject.semantic_dependencies,
                )
            )
            artifacts.append(artifact)

        ordered_jobs = tuple(sorted(jobs, key=lambda item: item.order))
        ordered_artifacts = tuple(sorted(artifacts, key=lambda item: order[item.job_id]))
        renderers = tuple(RendererRequirement(item) for item in sorted({job.renderer.capability for job in ordered_jobs}))
        pack_hashes = tuple(sorted((pack.instance_name, pack.manifest_hash) for pack in value.packs))
        placeholder = GenerationPlan(
            PLAN_VERSION,
            CONTEXT_VERSION,
            value.build_id,
            value.project_name,
            value.ir_hash,
            pack_hashes,
            renderers,
            ordered_jobs,
            ordered_artifacts,
            tuple(sorted(dependencies, key=lambda item: (item.job_id, item.depends_on_job_id, item.reason))),
            "",
        )
        semantic_document = placeholder.canonical_document(include_hash=False)
        semantic_document.pop("buildId", None)
        plan_hash = hash_plan(semantic_document)
        return replace(placeholder, plan_hash=plan_hash)


def _draft_jobs(value: PlanningInput) -> tuple[_Draft, ...]:
    drafts: list[_Draft] = []
    seen_paths: dict[str, str] = {}
    for pack in sorted(value.packs, key=lambda item: item.instance_name):
        selections = {item.key: item for item in pack.selections}
        for template in sorted(pack.templates, key=lambda item: item.key):
            selection = selections.get(template.selection)
            if selection is None:
                raise PlanningError("PLAN_SELECTION_MISSING", f"template {template.key!r} references missing selection {template.selection!r}")
            for subject in selected_subjects(selection.kind, value.subjects):
                job_id = f"{pack.instance_name}:{template.key}:{subject.id}"
                artifact_id = f"{job_id}:artifact"
                path = output_path(pack, template, subject)
                previous = seen_paths.get(path)
                if previous is not None:
                    raise PlanningError("PLAN_OUTPUT_COLLISION", f"jobs {previous!r} and {job_id!r} both produce {path!r}", subject=subject.id)
                seen_paths[path] = job_id
                drafts.append(
                    _Draft(
                        job_id,
                        subject,
                        pack,
                        selection,
                        template,
                        PlannedArtifact(artifact_id, path, job_id, (subject.id, *subject.semantic_dependencies)),
                    )
                )
    return tuple(sorted(drafts, key=lambda item: item.id))


def _resolve_dependencies(drafts: tuple[_Draft, ...]) -> tuple[PlanDependency, ...]:
    dependencies: list[PlanDependency] = []
    for draft in drafts:
        for template_key in draft.template.depends_on:
            matches = tuple(
                candidate
                for candidate in drafts
                if candidate.pack.instance_name == draft.pack.instance_name
                and candidate.template.key == template_key
                and (
                    candidate.subject.id == draft.subject.id
                    or candidate.subject.id in draft.subject.semantic_dependencies
                )
            )
            if not matches:
                raise PlanningError(
                    "PLAN_TEMPLATE_DEPENDENCY",
                    f"job {draft.id!r} cannot resolve required template dependency {template_key!r}",
                    subject=draft.subject.id,
                )
            for candidate in matches:
                dependencies.append(
                    PlanDependency(
                        draft.id,
                        candidate.id,
                        f"template {draft.template.key!r} depends on {template_key!r} for related semantic subject {candidate.subject.id}",
                    )
                )
    return tuple(dependencies)


def _order_jobs(ids: tuple[str, ...], dependencies: dict[str, tuple[str, ...]]) -> tuple[str, ...]:
    active: list[str] = []
    done: set[str] = set()
    result: list[str] = []

    def visit(identity: str) -> None:
        if identity in done:
            return
        if identity in active:
            cycle = " -> ".join((*active[active.index(identity):], identity))
            raise PlanningError("PLAN_JOB_CYCLE", f"render job dependency cycle: {cycle}", subject=identity)
        active.append(identity)
        try:
            for dependency in dependencies.get(identity, ()):
                visit(dependency)
        finally:
            active.pop()
        done.add(identity)
        result.append(identity)

    for identity in sorted(ids):
        visit(identity)
    return tuple(result)


def _context_size(context: JsonObject, job_id: str) -> None:
    encoded = json.dumps(context, ensure_ascii=False, allow_nan=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    if len(encoded) > _MAX_CONTEXT_BYTES:
        raise PlanningError("PLAN_CONTEXT_LIMIT", f"context for job {job_id!r} exceeds {_MAX_CONTEXT_BYTES} bytes", subject=job_id)


__all__ = ["PlanningFeature"]
