"""Variable resolver for template path expressions."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import Enum
from pathlib import Path
from typing import Any


class VariableResolutionError(KeyError):
    """Raised when a template path variable cannot be resolved."""


def resolve_variable(context: Mapping[str, Any], expression: str) -> Any:
    """Resolve dotted expressions like schema.name.path.o from context."""
    expression = expression.strip()

    if not expression:
        raise VariableResolutionError(expression)

    current: Any = context

    for part in expression.split("."):
        part = part.strip()

        if not part:
            raise VariableResolutionError(expression)

        current = _resolve_part(current, part, expression)

    return current


def stringify_value(value: Any) -> str:
    """Convert resolved values into safe path strings."""
    if value is None:
        return ""

    if isinstance(value, Enum):
        return str(value.value)

    if isinstance(value, Path):
        return value.as_posix()

    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, str):
        return value

    if isinstance(value, Sequence) and not isinstance(value, bytes | bytearray | str):
        return "-".join(stringify_value(item) for item in value)

    return str(value)


def _resolve_part(current: Any, part: str, expression: str) -> Any:
    if isinstance(current, Sequence) and not isinstance(current, bytes | bytearray | str):
        values: list[Any] = []
        for item in current:
            resolved = _resolve_part(item, part, expression)
            if isinstance(resolved, Sequence) and not isinstance(resolved, bytes | bytearray | str):
                values.extend(resolved)
            elif resolved is not None:
                values.append(resolved)
        return tuple(values)

    if isinstance(current, Mapping):
        if part not in current:
            raise VariableResolutionError(expression)
        return current[part]

    if hasattr(current, part):
        return getattr(current, part)

    raise VariableResolutionError(expression)
