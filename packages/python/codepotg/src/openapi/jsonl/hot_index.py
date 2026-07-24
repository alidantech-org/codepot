from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from threading import RLock
from typing import Generic, TypeVar

from .models import HotIndexLimits

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class HotIndexStats:
    entries: int
    estimated_bytes: int
    hits: int
    misses: int
    evictions: int


class BoundedHotIndex(Generic[T]):
    """Thread-safe LRU for small index facts, never raw JSONL records."""

    def __init__(
        self,
        limits: HotIndexLimits | None = None,
        *,
        estimate: Callable[[str, T], int] | None = None,
    ) -> None:
        self._limits = limits or HotIndexLimits()
        if self._limits.max_entries < 1:
            raise ValueError("max_entries must be at least 1")
        if self._limits.max_bytes < 1:
            raise ValueError("max_bytes must be at least 1")
        self._estimate = estimate or _estimate_value
        self._values: OrderedDict[str, tuple[T, int]] = OrderedDict()
        self._estimated_bytes = 0
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._lock = RLock()

    def get(self, key: str) -> T | None:
        with self._lock:
            stored = self._values.get(key)
            if stored is None:
                self._misses += 1
                return None
            self._values.move_to_end(key)
            self._hits += 1
            return stored[0]

    def put(self, key: str, value: T) -> bool:
        estimated = max(1, self._estimate(key, value))
        with self._lock:
            previous = self._values.pop(key, None)
            if previous is not None:
                self._estimated_bytes -= previous[1]

            if estimated > self._limits.max_bytes:
                return False

            self._values[key] = (value, estimated)
            self._estimated_bytes += estimated
            self._values.move_to_end(key)
            self._evict_to_limits()
            return key in self._values

    def discard(self, key: str) -> None:
        with self._lock:
            previous = self._values.pop(key, None)
            if previous is not None:
                self._estimated_bytes -= previous[1]

    def clear(self) -> None:
        with self._lock:
            self._values.clear()
            self._estimated_bytes = 0

    def stats(self) -> HotIndexStats:
        with self._lock:
            return HotIndexStats(
                entries=len(self._values),
                estimated_bytes=self._estimated_bytes,
                hits=self._hits,
                misses=self._misses,
                evictions=self._evictions,
            )

    def __len__(self) -> int:
        with self._lock:
            return len(self._values)

    def _evict_to_limits(self) -> None:
        while (
            len(self._values) > self._limits.max_entries
            or self._estimated_bytes > self._limits.max_bytes
        ):
            _, (_, estimated) = self._values.popitem(last=False)
            self._estimated_bytes -= estimated
            self._evictions += 1


def _estimate_value(key: str, value: object) -> int:
    return len(key.encode("utf-8")) + len(repr(value).encode("utf-8")) + 64


class HotIndexRegistry:
    """One bounded registry for definition aliases and cached index queries."""

    def __init__(self, limits: HotIndexLimits | None = None) -> None:
        self._index: BoundedHotIndex[object] = BoundedHotIndex(limits)

    @staticmethod
    def definition_key(lookup: str, value: str) -> str:
        return f"definition\0{lookup}\0{value}"

    @staticmethod
    def query_key(index: str, value: str) -> str:
        return f"query\0{index}\0{value}"

    def get_definition(self, lookup: str, value: str) -> object | None:
        return self._index.get(self.definition_key(lookup, value))

    def put_definition(self, lookup: str, value: str, location: object) -> bool:
        return self._index.put(self.definition_key(lookup, value), location)

    def get_query(self, index: str, value: str) -> object | None:
        return self._index.get(self.query_key(index, value))

    def put_query(self, index: str, value: str, facts: object) -> bool:
        return self._index.put(self.query_key(index, value), facts)

    def stats(self) -> HotIndexStats:
        return self._index.stats()

    def __len__(self) -> int:
        return len(self._index)
