from __future__ import annotations

from pathlib import PurePosixPath

from .contracts import PlanningError, PlanningPack, PlanningSubject, PlanningTemplate


def selected_subjects(kind: str, subjects: tuple[PlanningSubject, ...]) -> tuple[PlanningSubject, ...]:
    return tuple(sorted((item for item in subjects if item.kind == kind), key=lambda item: item.id))


def output_path(pack: PlanningPack, template: PlanningTemplate, subject: PlanningSubject) -> str:
    values = {
        "name": subject.name.name,
        "singular": subject.name.singular,
        "plural": subject.name.plural,
        "snake": subject.name.snake,
        "kebab": subject.name.kebab,
        "camel": subject.name.camel,
        "pascal": subject.name.pascal,
        "kind": subject.kind,
    }
    try:
        relative = template.output_pattern.format_map(values)
    except (KeyError, ValueError) as exc:
        raise PlanningError("PLAN_OUTPUT_PATTERN", f"cannot resolve output pattern for template {template.key!r}", subject=subject.id) from exc
    full = f"{pack.output_root.rstrip('/')}/{relative}"
    _safe_path(full)
    return full


def _safe_path(value: str) -> None:
    if not value or value.startswith("/") or "\\" in value:
        raise PlanningError("PLAN_OUTPUT_PATH", f"output path must be POSIX-relative: {value!r}")
    path = PurePosixPath(value)
    if any(part in {"", ".", ".."} for part in path.parts):
        raise PlanningError("PLAN_OUTPUT_PATH", f"output path contains an invalid segment: {value!r}")


__all__ = ["output_path", "selected_subjects"]
