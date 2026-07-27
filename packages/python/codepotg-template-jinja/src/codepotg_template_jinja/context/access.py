from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeAlias

SafeScalar: TypeAlias = str | int | float | bool | None
if TYPE_CHECKING:
    SafeValue: TypeAlias = "SafeScalar | tuple[SafeValue, ...] | SafeRecord"
else:
    SafeValue = object


@dataclass(frozen=True, slots=True)
class SafeRecord(Mapping[str, SafeValue]):
    """Minimal immutable mapping used as the only attribute-like template record."""

    _items: tuple[tuple[str, SafeValue], ...]

    def __post_init__(self) -> None:
        keys = tuple(key for key, _ in self._items)
        if tuple(sorted(keys)) != keys or len(keys) != len(set(keys)):
            raise ValueError("safe record keys must be sorted and unique")

    def __getitem__(self, key: str) -> SafeValue:
        for candidate, value in self._items:
            if candidate == key:
                return value
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return (key for key, _ in self._items)

    def __len__(self) -> int:
        return len(self._items)

    @property
    def fields(self) -> tuple[str, ...]:
        return tuple(key for key, _ in self._items)

    def as_tuple(self) -> tuple[tuple[str, SafeValue], ...]:
        return self._items
