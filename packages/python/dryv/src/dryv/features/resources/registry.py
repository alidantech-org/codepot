from __future__ import annotations

from hashlib import sha256

from .contracts import OriginMetadata, Resource, ResourceDescriptor, ResourceId

_DEFAULT_MAX_RESOURCE_BYTES = 64 * 1024 * 1024


class ResourceError(ValueError):
    def __init__(self, code: str, message: str, *, resource_id: ResourceId | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.resource_id = resource_id


class ResourceRegistry:
    """Bounded logical resources supplied explicitly to one Runtime build."""

    def __init__(self, *, max_resource_bytes: int = _DEFAULT_MAX_RESOURCE_BYTES) -> None:
        if max_resource_bytes < 1:
            raise ValueError("max_resource_bytes must be positive")
        self._max_resource_bytes = max_resource_bytes
        self._by_id: dict[ResourceId, Resource] = {}
        self._by_hash: dict[str, Resource] = {}

    def register_bytes(
        self,
        resource_id: ResourceId | str,
        media_type: str,
        content: bytes,
        *,
        content_hash: str | None = None,
        origin: OriginMetadata = (),
    ) -> Resource:
        identity = ResourceId(resource_id) if isinstance(resource_id, str) else resource_id
        if len(content) > self._max_resource_bytes:
            raise ResourceError("RESOURCE_LIMIT", f"resource exceeds {self._max_resource_bytes} bytes", resource_id=identity)
        computed = f"sha256:{sha256(content).hexdigest()}"
        if content_hash is not None and content_hash != computed:
            raise ResourceError("RESOURCE_HASH_MISMATCH", "supplied hash does not match resource bytes", resource_id=identity)
        resource = Resource(ResourceDescriptor(identity, media_type, len(content), computed, origin), bytes(content))
        existing = self._by_id.get(identity)
        if existing is not None:
            if existing != resource:
                raise ResourceError("RESOURCE_ID_CONFLICT", f"resource {identity} has conflicting content", resource_id=identity)
            return existing
        hashed = self._by_hash.get(computed)
        if hashed is not None and hashed.content != resource.content:
            raise ResourceError("RESOURCE_HASH_CONFLICT", f"hash collision for {computed}", resource_id=identity)
        self._by_id[identity] = resource
        self._by_hash.setdefault(computed, resource)
        return resource

    def get(self, resource_id: ResourceId | str) -> Resource | None:
        identity = ResourceId(resource_id) if isinstance(resource_id, str) else resource_id
        return self._by_id.get(identity)

    def require(self, resource_id: ResourceId | str) -> Resource:
        identity = ResourceId(resource_id) if isinstance(resource_id, str) else resource_id
        resource = self._by_id.get(identity)
        if resource is None:
            raise ResourceError("RESOURCE_MISSING", f"resource {identity} is not registered", resource_id=identity)
        return resource

    def by_hash(self, content_hash: str) -> Resource | None:
        return self._by_hash.get(content_hash)

    def ids(self) -> tuple[ResourceId, ...]:
        return tuple(sorted(self._by_id))


__all__ = ["ResourceError", "ResourceRegistry"]
