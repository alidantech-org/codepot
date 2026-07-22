"""Expand dynamic template paths into output paths."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from contracts.paths import PathTokenKind
from emission.templates.path_safety import validate_path_part, validate_relative_path
from emission.templates.path_tokens import parse_path_segment
from emission.templates.resolver import resolve_variable, stringify_value


def expand_template_path(
    template_path: Path,
    context: Mapping[str, Any],
    *,
    template_extension: str = ".j2",
) -> Path:
    """Expand a template-relative output path using a render context."""
    output_path = Path(*expand_template_parts(template_path.parts, context))
    output_path = _strip_template_suffix(output_path, template_extension)
    validate_relative_path(output_path)
    return output_path


def expand_template_parts(
    parts: tuple[Any, ...],
    context: Mapping[str, Any],
) -> tuple[str, ...]:
    """Expand dynamic template path parts without stripping template suffixes."""
    output_parts: list[str] = []

    for raw_part in parts:
        output_parts.extend(_expand_part(str(raw_part), context))

    return tuple(output_parts)


def _expand_part(raw_part: str, context: Mapping[str, Any]) -> list[str]:
    parsed = parse_path_segment(raw_part)

    if len(parsed.tokens) == 1:
        token = parsed.tokens[0]

        if token.kind == PathTokenKind.FOLDER:
            raise ValueError(f"folder recipe segment was not resolved before path expansion: {raw_part}")

        if token.kind == PathTokenKind.ESCAPED_DYNAMIC:
            return _validated_parts((f"[{token.expression}]",))

        if token.kind == PathTokenKind.ESCAPED_FOLDER:
            return _validated_parts((f"{{{token.expression}}}",))

        if token.kind == PathTokenKind.DYNAMIC and token.raw == raw_part:
            value = resolve_variable(context, token.expression)
            return _value_to_path_parts(value)

    value = _expand_inline(raw_part, context)
    return _validated_parts((value,))


def _value_to_path_parts(value: Any) -> list[str]:
    """Convert a resolved path value into one or more path parts."""
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return _validated_parts(tuple(stringify_value(item) for item in value))

    return _validated_parts((stringify_value(value),))


def _validated_parts(parts: tuple[str, ...]) -> list[str]:
    for part in parts:
        validate_path_part(part)

    return list(parts)


def _expand_inline(raw_part: str, context: Mapping[str, Any]) -> str:
    parsed = parse_path_segment(raw_part)
    result = raw_part

    for token in parsed.tokens:
        if token.kind == PathTokenKind.DYNAMIC:
            value = stringify_value(resolve_variable(context, token.expression))
            result = result.replace(token.raw, value)

        if token.kind == PathTokenKind.ESCAPED_DYNAMIC:
            result = result.replace(token.raw, f"[{token.expression}]")

        if token.kind == PathTokenKind.ESCAPED_FOLDER:
            result = result.replace(token.raw, f"{{{token.expression}}}")

    return result


def _strip_template_suffix(path: Path, template_extension: str) -> Path:
    text = path.as_posix()

    if text.endswith(template_extension):
        text = text[: -len(template_extension)]

    return Path(text)
