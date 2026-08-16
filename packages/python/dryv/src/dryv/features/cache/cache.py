from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CacheEntry:
    key: str
    value: bytes


class CacheFeature:
    """Small deterministic content cache; policy remains explicit at Runtime input."""

    def __init__(self) -> None:
        self._entries: dict[str, bytes] = {}

    def get(self, key: str) -> bytes | None:
        return self._entries.get(key)

    def put(self, key: str, value: bytes) -> CacheEntry:
        stored = bytes(value)
        self._entries[key] = stored
        return CacheEntry(key, stored)

    def clear(self) -> None:
        self._entries.clear()


__all__ = ["CacheEntry", "CacheFeature"]
