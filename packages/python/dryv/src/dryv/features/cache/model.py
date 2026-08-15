from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

CACHE_RECORD_VERSION = 1


class CacheMode(StrEnum):
    USE = "use"
    REFRESH = "refresh"
    OFF = "off"


class CacheStage(StrEnum):
    CONTEXT = "context"
    RENDER = "render"
    ARTIFACT = "artifact"


@dataclass(frozen=True, slots=True)
class ContextCacheKey:
    dependency_hashes: tuple[tuple[str, str], ...]
    projection_version: int
    pack_hash: str
    inputs_hash: str
    version: int = CACHE_RECORD_VERSION

    def __post_init__(self) -> None:
        if tuple(sorted(self.dependency_hashes)) != self.dependency_hashes:
            raise ValueError("context dependency hashes must be sorted")
        if self.version != CACHE_RECORD_VERSION or self.projection_version < 1:
            raise ValueError("unsupported context cache key version")


@dataclass(frozen=True, slots=True)
class RenderCacheKey:
    context_hash: str
    template_hash: str
    renderer_fingerprint_hash: str
    render_options_hash: str
    render_protocol_version: int
    context_version: int
    version: int = CACHE_RECORD_VERSION

    def __post_init__(self) -> None:
        if self.version != CACHE_RECORD_VERSION or self.render_protocol_version < 1 or self.context_version < 1:
            raise ValueError("unsupported render cache key version")


@dataclass(frozen=True, slots=True)
class ArtifactCacheKey:
    artifact_id: str
    build_input_hash: str
    version: int = CACHE_RECORD_VERSION


CacheKey = ContextCacheKey | RenderCacheKey | ArtifactCacheKey


@dataclass(frozen=True, slots=True)
class CacheEntry:
    stage: CacheStage
    key: CacheKey
    payload: bytes
    metadata: tuple[tuple[str, str], ...] = ()
    version: int = CACHE_RECORD_VERSION

    def __post_init__(self) -> None:
        if self.version != CACHE_RECORD_VERSION:
            raise ValueError("unsupported cache entry version")
        if tuple(sorted(self.metadata)) != self.metadata:
            raise ValueError("cache metadata must be sorted")


class CacheStore(Protocol):
    def get(self, stage: CacheStage, key: CacheKey) -> CacheEntry | None: ...
    def put(self, entry: CacheEntry) -> None: ...


class InMemoryCacheStore:
    def __init__(self) -> None:
        self._entries: dict[tuple[CacheStage, CacheKey], CacheEntry] = {}

    def get(self, stage: CacheStage, key: CacheKey) -> CacheEntry | None:
        return self._entries.get((stage, key))

    def put(self, entry: CacheEntry) -> None:
        self._entries[(entry.stage, entry.key)] = entry


class CacheTransaction:
    def __init__(self, store: CacheStore, mode: CacheMode, *, commit_enabled: bool) -> None:
        self._store = store
        self.mode = mode
        self._commit_enabled = commit_enabled
        self._pending: dict[tuple[CacheStage, CacheKey], CacheEntry] = {}
        self._closed = False

    def get(self, stage: CacheStage, key: CacheKey) -> CacheEntry | None:
        self._ensure_open()
        if self.mode is not CacheMode.USE:
            return None
        return self._pending.get((stage, key)) or self._store.get(stage, key)

    def put(self, entry: CacheEntry) -> None:
        self._ensure_open()
        if self.mode is CacheMode.OFF:
            return
        self._pending[(entry.stage, entry.key)] = entry

    def commit(self) -> None:
        self._ensure_open()
        try:
            if self.mode is not CacheMode.OFF and self._commit_enabled:
                for key in sorted(self._pending, key=lambda item: (item[0].value, repr(item[1]))):
                    self._store.put(self._pending[key])
        finally:
            self._pending.clear()
            self._closed = True

    def rollback(self) -> None:
        self._ensure_open()
        self._pending.clear()
        self._closed = True

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("cache transaction is closed")


class CacheFeature:
    def __init__(self, store: CacheStore | None = None) -> None:
        self.store = store or InMemoryCacheStore()

    def begin(self, mode: CacheMode, *, commit_enabled: bool = True) -> CacheTransaction:
        return CacheTransaction(self.store, mode, commit_enabled=commit_enabled)


__all__ = [
    "CACHE_RECORD_VERSION",
    "ArtifactCacheKey",
    "CacheEntry",
    "CacheFeature",
    "CacheMode",
    "CacheStage",
    "CacheStore",
    "CacheTransaction",
    "ContextCacheKey",
    "InMemoryCacheStore",
    "RenderCacheKey",
]
