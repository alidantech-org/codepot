from __future__ import annotations

import pytest

from dryv.features.planning import PlanningCandidate, PlanningError, PlanningFeature, TraceFact


def _candidate(**changes: object) -> PlanningCandidate:
    values: dict[str, object] = {
        "invocation_id": "invocation.a",
        "pack_id": "example/pack",
        "selection_key": "items",
        "template_resource_id": "resource://pack/example/item.jinja",
        "renderer_capability": "jinja/v1",
        "semantic_ids": ("schema.a",),
        "output_id": "artifact.a",
        "output_path": "src/a.ts",
        "context": {"schema": {"id": "schema.a", "name": "A"}},
        "semantic_dependencies": ("schema.a",),
        "trace": (TraceFact("selection", "schema.a", "matched items"),),
    }
    values.update(changes)
    return PlanningCandidate(**values)  # type: ignore[arg-type]


def test_plan_and_context_are_deterministic() -> None:
    feature = PlanningFeature()
    first = feature.build((_candidate(),))
    second = feature.build((_candidate(context={"schema": {"name": "A", "id": "schema.a"}}),))
    assert first.canonical_bytes() == second.canonical_bytes()
    assert first.artifact("artifact.a") is not None


def test_skipped_invocations_keep_explanation_without_artifact() -> None:
    plan = PlanningFeature().build((_candidate(enabled=False, skip_reason="condition false"),))
    assert plan.invocations[0].skip_reason == "condition false"
    assert plan.invocations[0].artifact_id is None
    assert plan.artifacts == ()


def test_artifact_dependencies_must_be_planned_and_acyclic() -> None:
    with pytest.raises(PlanningError) as missing:
        PlanningFeature().build((_candidate(artifact_dependencies=("artifact.missing",)),))
    assert missing.value.code == "PLAN_MISSING_ARTIFACT_DEPENDENCY"

    a = _candidate(artifact_dependencies=("artifact.b",))
    b = _candidate(invocation_id="invocation.b", output_id="artifact.b", output_path="src/b.ts", semantic_ids=("schema.b",), semantic_dependencies=("schema.b",), artifact_dependencies=("artifact.a",))
    with pytest.raises(PlanningError) as cycle:
        PlanningFeature().build((a, b))
    assert cycle.value.code == "PLAN_ARTIFACT_CYCLE"


def test_artifacts_are_emitted_in_dependency_order() -> None:
    dependent = _candidate(invocation_id="invocation.a", output_id="artifact.a", artifact_dependencies=("artifact.z",))
    provider = _candidate(invocation_id="invocation.z", output_id="artifact.z", output_path="src/z.ts", semantic_ids=("schema.z",), semantic_dependencies=("schema.z",))
    plan = PlanningFeature().build((dependent, provider))
    assert tuple(item.id for item in plan.artifacts) == ("artifact.z", "artifact.a")


def test_output_paths_cannot_escape_project_root() -> None:
    with pytest.raises(PlanningError) as caught:
        PlanningFeature().build((_candidate(output_path="../outside.ts"),))
    assert caught.value.code == "PLAN_OUTPUT_PATH"


def test_non_finite_context_numbers_are_structured_errors() -> None:
    with pytest.raises(PlanningError) as caught:
        PlanningFeature().build((_candidate(context={"value": float("nan")}),))
    assert caught.value.code == "PLAN_CONTEXT_NUMBER"
