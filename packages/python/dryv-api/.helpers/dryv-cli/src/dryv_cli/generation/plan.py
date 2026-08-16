from __future__ import annotations

from dryv_cli.artifacts import safe_artifact_path


class PlanDocumentError(ValueError):
    pass


def required_renderers(plan: dict[str, object]) -> tuple[str, ...]:
    raw = plan.get("requiredRenderers")
    if not isinstance(raw, list) or not all(isinstance(item, str) and item for item in raw):
        raise PlanDocumentError("GenerationPlan requiredRenderers must be an array of strings")
    if len(raw) != len(set(raw)):
        raise PlanDocumentError("GenerationPlan requiredRenderers must be unique")
    return tuple(raw)


def artifact_paths(plan: dict[str, object]) -> tuple[str, ...]:
    raw = plan.get("artifacts")
    if not isinstance(raw, list):
        raise PlanDocumentError("GenerationPlan artifacts must be an array")
    paths: list[str] = []
    for item in raw:
        if not isinstance(item, dict):
            raise PlanDocumentError("GenerationPlan artifact must be an object")
        path = item.get("path")
        if not isinstance(path, str) or not path:
            raise PlanDocumentError("GenerationPlan artifact requires a path")
        safe_artifact_path(path)
        paths.append(path)
    if len(paths) != len(set(paths)):
        raise PlanDocumentError("GenerationPlan artifact paths must be unique")
    return tuple(paths)


def plan_hash(plan: dict[str, object]) -> str:
    value = plan.get("planHash")
    if not isinstance(value, str) or not value:
        raise PlanDocumentError("GenerationPlan requires planHash")
    return value


__all__ = ["PlanDocumentError", "artifact_paths", "plan_hash", "required_renderers"]
