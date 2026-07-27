from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeAlias

SafeScalar: TypeAlias = str | int | float | bool | None
if TYPE_CHECKING:
    SafeValue: TypeAlias = SafeScalar | tuple["SafeValue", ...] | SafeRecord
else:
    SafeValue = object

_TAG_METHODS = frozenset({"has", "has_any", "has_all", "under"})


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

    @property
    def is_tag_set(self) -> bool:
        if self.fields != ("values",):
            return False
        values = self["values"]
        return isinstance(values, tuple) and all(isinstance(item, str) for item in values)

    @property
    def empty(self) -> bool:
        return not self._tag_values()

    def has(self, tag: str) -> bool:
        return tag in self._tag_values()

    def has_any(self, *tags: str) -> bool:
        values = self._tag_values()
        return any(tag in values for tag in tags)

    def has_all(self, *tags: str) -> bool:
        values = self._tag_values()
        return all(tag in values for tag in tags)

    def under(self, namespace: str) -> tuple[str, ...]:
        values = self._tag_values()
        prefix = f"{namespace}:"
        return tuple(tag for tag in values if tag == namespace or tag.startswith(prefix))

    def is_allowed_tag_attribute(self, attribute: str) -> bool:
        return self.is_tag_set and (attribute in _TAG_METHODS or attribute == "empty")

    def as_tuple(self) -> tuple[tuple[str, SafeValue], ...]:
        return self._items

    def _tag_values(self) -> tuple[str, ...]:
        if not self.is_tag_set:
            raise TypeError("tag query methods are available only on TagSet records")
        values = self["values"]
        assert isinstance(values, tuple)
        return values
