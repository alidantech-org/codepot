from __future__ import annotations

from dataclasses import dataclass

from .ids import ResourceId

ContentHash = str
OriginMetadata = tuple[tuple[str, str], ...]
_HASH_PREFIX = "sha256:"


@dataclass(frozen=True, slots=True)
class ResourceDescriptor:
    id: ResourceId
    media_type: str
    size: int | None = None
    content_hash: ContentHash | None = None
    origin: OriginMetadata = ()

    def __post_init__(self) -> None:
        if not self.media_type or self.media_type.strip() != self.media_type or any(character.isspace() for character in self.media_type):
            raise ValueError("resource media type must be a non-empty token")
        if self.size is not None and self.size < 0:
            raise ValueError("resource size must be non-negative")
        if self.content_hash is not None:
            validate_content_hash(self.content_hash)
        keys = tuple(key for key, _ in self.origin)
        if tuple(sorted(keys)) != keys or len(keys) != len(set(keys)):
            raise ValueError("resource origin metadata must be sorted by unique key")
        if any(not key or not value for key, value in self.origin):
            raise ValueError("resource origin metadata keys and values must be non-empty")


@dataclass(frozen=True, slots=True)
class ResourceManifestEntry:
    id: ResourceId
    media_type: str | None = None
    size: int | None = None
    content_hash: ContentHash | None = None

    def __post_init__(self) -> None:
        if self.media_type is not None and (not self.media_type or self.media_type.strip() != self.media_type):
            raise ValueError("manifest media type must be a trimmed string")
        if self.size is not None and self.size < 0:
            raise ValueError("manifest resource size must be non-negative")
        if self.content_hash is not None:
            validate_content_hash(self.content_hash)


@dataclass(frozen=True, slots=True)
class ResourceManifest:
    entries: tuple[ResourceManifestEntry, ...] = ()

    def __post_init__(self) -> None:
        ordered = tuple(sorted(self.entries, key=lambda item: item.id.value))
        ids = tuple(item.id for item in ordered)
        if len(ids) != len(set(ids)):
            raise ValueError("resource manifest logical ids must be unique")
        object.__setattr__(self, "entries", ordered)

    def by_id(self, resource: ResourceId | str) -> ResourceManifestEntry | None:
        target = ResourceId(resource) if isinstance(resource, str) else resource
        return next((item for item in self.entries if item.id == target), None)


@dataclass(frozen=True, slots=True)
class Resource:
    descriptor: ResourceDescriptor
    content: bytes

    def __post_init__(self) -> None:
        if self.descriptor.size is not None and self.descriptor.size != len(self.content):
            raise ValueError("resource descriptor size does not match supplied content")


def validate_content_hash(value: str) -> None:
    if not value.startswith(_HASH_PREFIX):
        raise ValueError("content hash must use sha256:<hex>")
    digest = value.removeprefix(_HASH_PREFIX)
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise ValueError("content hash must contain a lowercase SHA-256 digest")


__all__ = ["ContentHash", "OriginMetadata", "Resource", "ResourceDescriptor", "ResourceManifest", "ResourceManifestEntry", "validate_content_hash"]
