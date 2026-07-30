"""Immutable source-value contracts used for lossless template access."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any


class FrozenMap(Mapping[str, Any]):
    """Recursively immutable mapping that remains friendly to Jinja and deepcopy."""

    __slots__ = ("_data",)

    def __init__(self, values: Mapping[str, Any] | None = None) -> None:
        self._data = {
            str(key): freeze_source_value(value)
            for key, value in (values or {}).items()
        }

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"FrozenMap({self._data!r})"

    def __deepcopy__(self, memo: dict[int, Any]) -> FrozenMap:
        """Immutable instances can be reused safely by dataclass serializers."""
        memo[id(self)] = self
        return self

    def to_dict(self) -> dict[str, Any]:
        """Return a mutable deep copy suitable for JSON/YAML serialization."""
        return {key: thaw_source_value(value) for key, value in self._data.items()}


def freeze_source_map(values: Mapping[str, Any] | None) -> FrozenMap:
    """Recursively freeze a source mapping."""
    if isinstance(values, FrozenMap):
        return values
    return FrozenMap(values)


def freeze_source_value(value: Any) -> Any:
    """Recursively freeze mappings and sequences while preserving scalar values."""
    if isinstance(value, FrozenMap):
        return value
    if isinstance(value, Mapping):
        return FrozenMap(value)
    if isinstance(value, list | tuple):
        return tuple(freeze_source_value(item) for item in value)
    if isinstance(value, set | frozenset):
        return frozenset(freeze_source_value(item) for item in value)
    return value


def thaw_source_value(value: Any) -> Any:
    """Convert immutable source values back to ordinary mutable containers."""
    if isinstance(value, FrozenMap):
        return value.to_dict()
    if isinstance(value, tuple):
        return [thaw_source_value(item) for item in value]
    if isinstance(value, frozenset):
        return [thaw_source_value(item) for item in value]
    return value
