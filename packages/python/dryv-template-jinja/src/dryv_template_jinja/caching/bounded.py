from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from threading import RLock
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class CacheStats:
    entries: int
    hits: int
    misses: int
    evictions: int


class BoundedCache(Generic[T]):
    def __init__(self, capacity: int) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity < 1:
            raise ValueError("cache capacity must be a positive integer")
        self._capacity = capacity
        self._items: OrderedDict[str, T] = OrderedDict()
        self._lock = RLock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, key: str) -> T | None:
        with self._lock:
            try:
                value = self._items.pop(key)
            except KeyError:
                self._misses += 1
                return None
            self._items[key] = value
            self._hits += 1
            return value

    def put(self, key: str, value: T) -> None:
        with self._lock:
            self._items.pop(key, None)
            self._items[key] = value
            while len(self._items) > self._capacity:
                self._items.popitem(last=False)
                self._evictions += 1

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def stats(self) -> CacheStats:
        with self._lock:
            return CacheStats(
                entries=len(self._items),
                hits=self._hits,
                misses=self._misses,
                evictions=self._evictions,
            )
