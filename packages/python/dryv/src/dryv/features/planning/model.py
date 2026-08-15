from __future__ import annotations

import json
import math
from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping, Sequence, TypeAlias

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]

PLAN_VERSION = 1
CONTEXT_VERSION = 1


class PlanningError(ValueError):
    def __init__(self, code: str, message: str, *, subject: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.subject = subject


class InvocationStatus(StrEnum):
    PLANNED = "planned"
    SKIPPED = "skipped"


@dataclass(frozen=True, slots=True)
class TraceFact:
    kind: str
    subject: str
    reason: str


@dataclass(frozen=True, slots=True)
class PlanningCandidate:
    invocation_id: str
    pack_id: str
    selection_key: str
    template_resource_id: str
    renderer_capability: str
    semantic_ids: tuple[str, ...]
    output_id: str
    output_path: str
    context: Mapping[str, JsonValue]
    semantic_dependencies: tuple[str, ...]
    artifact_dependencies: tuple[str, ...] = ()
    enabled: bool = True
    skip_reason: str | None = None
    options_used: tuple[str, ...] = ()
    bindings_used: tuple[str, ...] = ()
    trace: tuple[TraceFact, ...] = ()


@dataclass(frozen=True, slots=True)
class PlannedArtifact:
    id: str
    path: str
    invocation_id: str
    semantic_ids: tuple[str, ...]
    dependencies: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PlannedInvocation:
    id: str
    status: InvocationStatus
    pack_id: str
    selection_key: str
    template_resource_id: str
    renderer_capability: str
    semantic_ids: tuple[str, ...]
    context: JsonValue | None
    semantic_dependencies: tuple[str, ...]
    artifact_id: str | None
    skip_reason: str | None
    options_used: tuple[str, ...]
    bindings_used: tuple[str, ...]
    trace: tuple[TraceFact, ...]


@dataclass(frozen=True, slots=True)
class GenerationPlan:
    version: int
    context_version: int
    invocations: tuple[PlannedInvocation, ...]
    artifacts: tuple[PlannedArtifact, ...]

    def artifact(self, identity: str) -> PlannedArtifact | None:
        return next((item for item in self.artifacts if item.id == identity), None)

    def canonical_document(self) -> dict[str, JsonValue]:
        return {
            "contextVersion": self.context_version,
            "planVersion": self.version,
            "artifacts": [
                {
                    "dependencies": list(item.dependencies),
                    "id": item.id,
                    "invocationId": item.invocation_id,
                    "path": item.path,
                    "semanticIds": list(item.semantic_ids),
                }
                for item in self.artifacts
            ],
            "invocations": [
                {
                    "artifactId": item.artifact_id,
                    "bindingsUsed": list(item.bindings_used),
                    "context": item.context,
                    "id": item.id,
                    "optionsUsed": list(item.options_used),
                    "packId": item.pack_id,
                    "rendererCapability": item.renderer_capability,
                    "selectionKey": item.selection_key,
                    "semanticDependencies": list(item.semantic_dependencies),
                    "semanticIds": list(item.semantic_ids),
                    "skipReason": item.skip_reason,
                    "status": item.status.value,
                    "templateResourceId": item.template_resource_id,
                    "trace": [
                        {"kind": fact.kind, "reason": fact.reason, "subject": fact.subject}
                        for fact in item.trace
                    ],
                }
                for item in self.invocations
            ],
        }

    def canonical_bytes(self) -> bytes:
        return json.dumps(
            self.canonical_document(),
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")


class PlanningFeature:
    def __init__(self, *, max_context_bytes: int = 2 * 1024 * 1024) -> None:
        self._max_context_bytes = max_context_bytes

    def build(self, candidates: Sequence[PlanningCandidate]) -> GenerationPlan:
        ordered = tuple(sorted(candidates, key=lambda item: item.invocation_id))
        ids = tuple(item.invocation_id for item in ordered)
        if len(ids) != len(set(ids)):
            raise PlanningError("PLAN_DUPLICATE_INVOCATION", "invocation ids must be unique")

        invocations: list[PlannedInvocation] = []
        artifacts: list[PlannedArtifact] = []
        artifact_ids: set[str] = set()
        for item in ordered:
            _safe_path(item.output_path)
            semantic_ids = tuple(sorted(set(item.semantic_ids)))
            semantic_dependencies = tuple(sorted(set(item.semantic_dependencies)))
            artifact_dependencies = tuple(sorted(set(item.artifact_dependencies)))
            trace = tuple(sorted(item.trace, key=lambda fact: (fact.kind, fact.subject, fact.reason)))
            if not item.enabled:
                if not item.skip_reason:
                    raise PlanningError("PLAN_SKIP_REASON", "skipped invocations require a reason", subject=item.invocation_id)
                invocations.append(PlannedInvocation(
                    item.invocation_id, InvocationStatus.SKIPPED, item.pack_id, item.selection_key,
                    item.template_resource_id, item.renderer_capability, semantic_ids, None,
                    semantic_dependencies, None, item.skip_reason,
                    tuple(sorted(set(item.options_used))), tuple(sorted(set(item.bindings_used))), trace,
                ))
                continue

            if item.output_id in artifact_ids:
                raise PlanningError("PLAN_DUPLICATE_ARTIFACT", f"duplicate planned artifact {item.output_id!r}", subject=item.output_id)
            artifact_ids.add(item.output_id)
            context = _canonical_context(item.context, self._max_context_bytes)
            artifacts.append(PlannedArtifact(item.output_id, item.output_path, item.invocation_id, semantic_ids, artifact_dependencies))
            invocations.append(PlannedInvocation(
                item.invocation_id, InvocationStatus.PLANNED, item.pack_id, item.selection_key,
                item.template_resource_id, item.renderer_capability, semantic_ids, context,
                semantic_dependencies, item.output_id, None,
                tuple(sorted(set(item.options_used))), tuple(sorted(set(item.bindings_used))), trace,
            ))

        known = {item.id for item in artifacts}
        for artifact in artifacts:
            missing = tuple(dep for dep in artifact.dependencies if dep not in known)
            if missing:
                raise PlanningError("PLAN_MISSING_ARTIFACT_DEPENDENCY", f"artifact {artifact.id!r} depends on missing artifact {missing[0]!r}", subject=artifact.id)
        ordered_artifacts = _order_artifacts(artifacts)
        return GenerationPlan(PLAN_VERSION, CONTEXT_VERSION, tuple(invocations), ordered_artifacts)


def _canonical_context(value: Mapping[str, JsonValue], max_bytes: int) -> dict[str, JsonValue]:
    normalized = _normalize(dict(value))
    assert isinstance(normalized, dict)
    encoded = json.dumps(normalized, ensure_ascii=False, allow_nan=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    if len(encoded) > max_bytes:
        raise PlanningError("PLAN_CONTEXT_LIMIT", f"template context exceeds {max_bytes} bytes")
    return normalized


def _normalize(value: object) -> JsonValue:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise PlanningError("PLAN_CONTEXT_NUMBER", "context numbers must be finite")
        return value
    if isinstance(value, list | tuple):
        return [_normalize(item) for item in value]
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise PlanningError("PLAN_CONTEXT_KEY", "context object keys must be strings")
        return {key: _normalize(value[key]) for key in sorted(value)}
    raise PlanningError("PLAN_CONTEXT_VALUE", f"context contains unsupported value {type(value).__name__}")


def _safe_path(path: str) -> None:
    normalized = path.replace("\\", "/")
    if not normalized or normalized.startswith("/") or ":" in normalized.split("/", 1)[0] or any(part in {"", ".", ".."} for part in normalized.split("/")):
        raise PlanningError("PLAN_OUTPUT_PATH", f"output path must be a safe project-relative path: {path!r}")


def _order_artifacts(artifacts: Sequence[PlannedArtifact]) -> tuple[PlannedArtifact, ...]:
    by_id = {item.id: item for item in artifacts}
    active: list[str] = []
    done: set[str] = set()
    result: list[PlannedArtifact] = []

    def visit(identity: str) -> None:
        if identity in done:
            return
        if identity in active:
            cycle = " -> ".join((*active[active.index(identity):], identity))
            raise PlanningError("PLAN_ARTIFACT_CYCLE", f"artifact dependency cycle: {cycle}", subject=identity)
        active.append(identity)
        try:
            for dependency in by_id[identity].dependencies:
                visit(dependency)
        finally:
            active.pop()
        done.add(identity)
        result.append(by_id[identity])

    for identity in sorted(by_id):
        visit(identity)
    return tuple(result)


__all__ = [
    "CONTEXT_VERSION",
    "GenerationPlan",
    "InvocationStatus",
    "JsonValue",
    "PLAN_VERSION",
    "PlannedArtifact",
    "PlannedInvocation",
    "PlanningCandidate",
    "PlanningError",
    "PlanningFeature",
    "TraceFact",
]
