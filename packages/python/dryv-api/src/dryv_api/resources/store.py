from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from dryv.runtime import RuntimeResource

from dryv_api.contracts import ApiContractError, BuildResourceUpload

_MAX_RESOURCE_BYTES = 64 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class StoredResource:
    resource_id: str
    media_type: str
    content: bytes
    content_hash: str

    def runtime_resource(self) -> RuntimeResource:
        return RuntimeResource(
            self.resource_id,
            self.media_type,
            self.content,
            self.content_hash,
        )


class ResourceStore:
    """Build-scoped, server-verified logical resource storage for stateless V1."""

    def __init__(self, *, max_resource_bytes: int = _MAX_RESOURCE_BYTES) -> None:
        if max_resource_bytes < 1:
            raise ValueError("max_resource_bytes must be positive")
        self._max_resource_bytes = max_resource_bytes
        self._by_id: dict[str, StoredResource] = {}
        self._by_hash: dict[str, StoredResource] = {}

    def add(self, upload: BuildResourceUpload) -> StoredResource:
        if len(upload.content) > self._max_resource_bytes:
            raise ApiContractError(
                "API_RESOURCE_LIMIT",
                f"resource {upload.resource_id!r} exceeds {self._max_resource_bytes} bytes",
            )
        digest = f"sha256:{sha256(upload.content).hexdigest()}"
        if upload.content_hash is not None and upload.content_hash != digest:
            raise ApiContractError(
                "API_RESOURCE_HASH_MISMATCH",
                f"claimed hash for {upload.resource_id!r} does not match uploaded bytes",
            )
        stored = StoredResource(upload.resource_id, upload.media_type, bytes(upload.content), digest)
        previous = self._by_id.get(upload.resource_id)
        if previous is not None:
            if previous != stored:
                raise ApiContractError(
                    "API_RESOURCE_ID_CONFLICT",
                    f"resource id {upload.resource_id!r} was uploaded with different content",
                )
            return previous
        same_hash = self._by_hash.get(digest)
        if same_hash is not None and same_hash.content != stored.content:
            raise ApiContractError("API_RESOURCE_HASH_CONFLICT", f"content hash collision for {digest}")
        self._by_id[upload.resource_id] = stored
        self._by_hash.setdefault(digest, stored)
        return stored

    def require(self, resource_id: str) -> StoredResource:
        resource = self._by_id.get(resource_id)
        if resource is None:
            raise ApiContractError("API_RESOURCE_MISSING", f"resource {resource_id!r} is not available")
        return resource

    def resources(self) -> tuple[StoredResource, ...]:
        return tuple(self._by_id[key] for key in sorted(self._by_id))


__all__ = ["ResourceStore", "StoredResource"]
