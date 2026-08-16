from __future__ import annotations

from collections.abc import Callable

from .contracts import (
    CONTEXT_CONTRACT_VERSION,
    ContextContract,
    JsonObject,
    JsonValue,
    PlannedArtifact,
    PlanningPack,
    PlanningSelection,
    PlanningSubject,
)


def build_context(
    *,
    project_name: str,
    subject: PlanningSubject,
    semantic_dependencies: tuple[PlanningSubject, ...],
    dependency_artifacts: tuple[PlannedArtifact, ...],
    artifact: PlannedArtifact,
    pack: PlanningPack,
    selection: PlanningSelection,
) -> JsonObject:
    return {
        "project": {"name": project_name},
        "subject": subject.value,
        "subjectId": subject.id,
        "subjectKind": subject.kind,
        "effective": subject.effective,
        "dependencies": {
            item.id: item.value for item in semantic_dependencies
        },
        "artifact": {"id": artifact.id, "path": artifact.path},
        "artifacts": {
            "dependencies": [
                {"id": item.id, "jobId": item.job_id, "path": item.path}
                for item in dependency_artifacts
            ]
        },
        "pack": {
            "id": pack.pack_id,
            "instance": pack.instance_name,
            "version": pack.version,
            "options": pack.options,
            "bindings": pack.bindings,
        },
        "selection": {
            "key": selection.key,
            "symbols": list(selection.symbols),
        },
    }


def context_contract(context: JsonObject, *, hasher: Callable[[JsonValue], str]) -> ContextContract:
    paths = tuple(sorted(_paths(context, "$")))
    digest = hasher({"version": CONTEXT_CONTRACT_VERSION, "paths": list(paths)})
    return ContextContract(CONTEXT_CONTRACT_VERSION, paths, digest)


def _paths(value: JsonValue, path: str) -> set[str]:
    result = {path}
    if isinstance(value, dict):
        for key, item in value.items():
            result.update(_paths(item, f"{path}.{key}"))
    elif isinstance(value, list):
        wildcard = f"{path}[*]"
        result.add(wildcard)
        for item in value:
            result.update(_paths(item, wildcard))
    return result


__all__ = ["build_context", "context_contract"]
