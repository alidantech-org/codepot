from __future__ import annotations

from codepotg.ir import FieldConstraints

from ..parsing.document import ParsedDocument
from .context import NormalizationContext
from .groups import component_group


def field_constraints(value: dict[str, object]) -> FieldConstraints:
    origins: list[tuple[str, str]] = []
    kwargs: dict[str, object] = {}
    for source, target in (
        ("minimum", "minimum"),
        ("maximum", "maximum"),
        ("minLength", "min_length"),
        ("maxLength", "max_length"),
        ("pattern", "pattern"),
        ("format", "format"),
    ):
        item = value.get(source)
        if target in {"pattern", "format"}:
            valid = isinstance(item, str)
        elif target in {"min_length", "max_length"}:
            valid = isinstance(item, int) and not isinstance(item, bool)
        else:
            valid = isinstance(item, int | float) and not isinstance(item, bool)
        if valid:
            kwargs[target] = item
            origins.append((target, f"openapi:{source}"))
    return FieldConstraints(**kwargs, origins=tuple(sorted(origins)))


def schema_types(value: object) -> tuple[bool, tuple[str, ...]]:
    if isinstance(value, str):
        return value == "null", () if value == "null" else (value,)
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        nullable = "null" in value
        return nullable, tuple(item for item in value if item != "null")
    return False, ()


def pointer_hint(pointer: str, fallback: str) -> str:
    if pointer:
        segment = pointer.rsplit("/", 1)[-1].replace("~1", "/").replace("~0", "~")
        if segment:
            return segment
    return fallback


def referenced_group(
    context: NormalizationContext,
    document: ParsedDocument,
    pointer: str,
    hint: str,
) -> str:
    if document is context.root and pointer.startswith("/components/schemas/"):
        return component_group(context, hint)
    return "shared"


def title(value: str) -> str:
    return "".join(
        part[:1].upper() + part[1:] for part in value.replace("-", "_").split("_") if part
    )
