"""Safe debug serialization helpers for pipeline snapshots."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any

MAX_DEPTH = 12


def _primitive(value: object) -> bool:
    """Return true when value is directly JSON-compatible."""

    return value is None or isinstance(value, str | int | float | bool)


def _enum(value: Enum) -> str:
    """Serialize enum values."""

    return str(value.value)


def _path(value: Path) -> str:
    """Serialize paths as POSIX text."""

    return value.as_posix()


def _sequence(
    value: tuple[object, ...] | list[object],
    *,
    depth: int,
) -> list[object]:
    """Serialize a sequence."""

    return [to_debug_json(item, depth=depth + 1) for item in value]


def _mapping(
    value: dict[object, object],
    *,
    depth: int,
) -> dict[str, object]:
    """Serialize a mapping."""

    return {
        str(key): to_debug_json(item, depth=depth + 1)
        for key, item in value.items()
    }


def _dataclass(
    value: object,
    *,
    depth: int,
) -> dict[str, object]:
    """Serialize dataclass fields directly."""

    return {
        field.name: to_debug_json(getattr(value, field.name), depth=depth + 1)
        for field in fields(value)
    }


def _pydantic_model(
    value: Any,
    *,
    depth: int,
) -> object:
    """Serialize a pydantic model if available."""

    dumped = value.model_dump(mode="json", by_alias=True)
    return to_debug_json(dumped, depth=depth + 1)


def to_debug_json(value: object, *, depth: int = 0) -> object:
    """Convert a value into JSON-compatible debug data."""

    if depth > MAX_DEPTH:
        return "<max-depth>"

    if _primitive(value):
        return value

    if isinstance(value, Enum):
        return _enum(value)

    if isinstance(value, Path):
        return _path(value)

    if isinstance(value, tuple | list):
        return _sequence(value, depth=depth)

    if isinstance(value, dict):
        return _mapping(value, depth=depth)

    if is_dataclass(value) and not isinstance(value, type):
        return _dataclass(value, depth=depth)

    if hasattr(value, "model_dump"):
        return _pydantic_model(value, depth=depth)

    return repr(value)
