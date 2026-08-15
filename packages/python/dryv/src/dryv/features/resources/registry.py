from __future__ import annotations

from hashlib import sha256
from typing import BinaryIO, Iterable, Iterator

from .ids import ResourceId
from .models import OriginMetadata, Resource, ResourceDescriptor, ResourceManifest, ResourceManifestEntry

_DEFAULT_MAX_RESOURCE_BYTES = 64 * 1024 * 1024
_DEFAULT_CHUNK_BYTES = 64 * 1024


class ResourceError(ValueError):
    def __init__(self, code: str, message: str, *, resource_id: ResourceId | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.resource_id = resource_id


class ResourceRegistry:
    """In-memory logical/content-addressed resources supplied to Dryv Engine."""

    def __init__(self, *, max_resource_bytes: int = _DEFAULT_MAX_RESOURCE_BYTES) -> None:
        if max_resource_bytes < 1:
            raise ValueError("max_resource_bytes must be positive")
        self._max_resource_bytes = max_resource_bytes
        self._by_id: dict[ResourceId, Resource] = {}
        self._by_hash: dict[str, Resource] = {}

    @property
    def manifest(self) -> ResourceManifest:
        return ResourceManifest(tuple(ResourceManifestEntry(resource.descriptor.id, resource.descriptor.media_type, resource.descriptor.size, resource.descriptor.content_hash) for resource in self._by_id.values()))

    def register_bytes(self, resource_id: ResourceId | str, media_type: str, content: bytes, *, content_hash: str | None = None, origin: OriginMetadata = ()) -> Resource:
        identity = ResourceId(resource_id) if isinstance(resource_id, str) else resource_id
        if len(content) > self._max_resource_bytes:
            raise ResourceError("RESOURCE_LIMIT", f"resource exceeds {self._max_resource_bytes} bytes", resource_id=identity)
        computed = _content_hash(content)
        if content_hash is not None and content_hash != computed:
            raise ResourceError("RESOURCE_HASH_MISMATCH", "supplied content hash does not match resource bytes", resource_id=identity)
        descriptor = ResourceDescriptor(identity, media_type, len(content), computed, origin)
        resource = Resource(descriptor, bytes(content))
        return self._register(resource)

    def register_stream(self, resource_id: ResourceId | str, media_type: str, stream: BinaryIO | Iterable[bytes], *, content_hash: str | None = None, origin: OriginMetadata = (), chunk_bytes: int = _DEFAULT_CHUNK_BYTES) -> Resource:
        if chunk_bytes < 1:
            raise ValueError("chunk_bytes must be positive")
        identity = ResourceId(resource_id) if isinstance(resource_id, str) else resource_id
        chunks: list[bytes] = []
        total = 0
        iterable = _read_chunks(stream, chunk_bytes) if hasattr(stream, "read") else stream  # type: ignore[arg-type]
        for chunk in iterable:
            if not isinstance(chunk, bytes):
                raise ResourceError("RESOURCE_STREAM_CHUNK", "resource stream chunks must be bytes", resource_id=identity)
            total += len(chunk)
            if total > self._max_resource_bytes:
                raise ResourceError("RESOURCE_LIMIT", f"resource exceeds {self._max_resource_bytes} bytes", resource_id=identity)
            chunks.append(chunk)
        return self.register_bytes(identity, media_type, b"".join(chunks), content_hash=content_hash, origin=origin)

    def get(self, resource_id: ResourceId | str) -> Resource | None:
        identity = ResourceId(resource_id) if isinstance(resource_id, str) else resource_id
        return self._by_id.get(identity)

    def get_by_hash(self, content_hash: str) -> Resource | None:
        return self._by_hash.get(content_hash)

    def require(self, resource_id: ResourceId | str) -> Resource:
        identity = ResourceId(resource_id) if isinstance(resource_id, str) else resource_id
        resource = self._by_id.get(identity)
        if resource is None:
            raise ResourceError("RESOURCE_MISSING", f"resource {identity} is not registered", resource_id=identity)
        return resource

    def read(self, resource_id: ResourceId | str, *, max_bytes: int | None = None) -> bytes:
        resource = self.require(resource_id)
        limit = self._max_resource_bytes if max_bytes is None else max_bytes
        if limit < 0:
            raise ValueError("max_bytes must be non-negative")
        if len(resource.content) > limit:
            raise ResourceError("RESOURCE_READ_LIMIT", f"resource exceeds read limit {limit} bytes", resource_id=resource.descriptor.id)
        return resource.content

    def iter_bytes(self, resource_id: ResourceId | str, *, chunk_bytes: int = _DEFAULT_CHUNK_BYTES, max_bytes: int | None = None) -> Iterator[bytes]:
        if chunk_bytes < 1:
            raise ValueError("chunk_bytes must be positive")
        resource = self.require(resource_id)
        limit = self._max_resource_bytes if max_bytes is None else max_bytes
        if limit < 0:
            raise ValueError("max_bytes must be non-negative")
        if len(resource.content) > limit:
            raise ResourceError("RESOURCE_READ_LIMIT", f"resource exceeds read limit {limit} bytes", resource_id=resource.descriptor.id)
        for offset in range(0, len(resource.content), chunk_bytes):
            yield resource.content[offset : offset + chunk_bytes]

    def missing(self, manifest: ResourceManifest) -> tuple[ResourceManifestEntry, ...]:
        missing: list[ResourceManifestEntry] = []
        for entry in manifest.entries:
            by_id = self._by_id.get(entry.id)
            if by_id is not None:
                if entry.content_hash is not None and by_id.descriptor.content_hash != entry.content_hash:
                    raise ResourceError("RESOURCE_MANIFEST_CONFLICT", f"registered resource {entry.id} has a different content hash", resource_id=entry.id)
                continue
            if entry.content_hash is not None and entry.content_hash in self._by_hash:
                continue
            missing.append(entry)
        return tuple(missing)

    def missing_hashes(self, manifest: ResourceManifest) -> tuple[str, ...]:
        hashes = {entry.content_hash for entry in self.missing(manifest) if entry.content_hash is not None}
        return tuple(sorted(hashes))

    def _register(self, resource: Resource) -> Resource:
        identity = resource.descriptor.id
        digest = resource.descriptor.content_hash
        assert digest is not None
        existing = self._by_id.get(identity)
        if existing is not None:
            if existing.descriptor.media_type != resource.descriptor.media_type or existing.content != resource.content:
                raise ResourceError("RESOURCE_ID_CONFLICT", f"resource id {identity} is already registered with different content or media type", resource_id=identity)
            return existing
        hashed = self._by_hash.get(digest)
        if hashed is not None and hashed.content != resource.content:
            raise ResourceError("RESOURCE_HASH_CONFLICT", f"content hash {digest} is already registered for different bytes", resource_id=identity)
        self._by_id[identity] = resource
        self._by_hash.setdefault(digest, resource)
        return resource


def _content_hash(content: bytes) -> str:
    return f"sha256:{sha256(content).hexdigest()}"


def _read_chunks(stream: BinaryIO, chunk_bytes: int) -> Iterator[bytes]:
    while True:
        chunk = stream.read(chunk_bytes)
        if not chunk:
            return
        yield chunk


__all__ = ["ResourceError", "ResourceRegistry"]
