from __future__ import annotations

from dataclasses import dataclass

ContentHash = str
OriginMetadata = tuple[tuple[str, str], ...]
_HASH_PREFIX = "sha256:"


class ResourceIdError(ValueError):
    pass


@dataclass(frozen=True, slots=True, order=True)
class ResourceId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", normalize_resource_id(self.value))

    @property
    def namespace(self) -> str:
        return self.value.removeprefix("resource://").split("/", 1)[0]

    @property
    def path(self) -> str:
        return self.value.removeprefix("resource://").split("/", 1)[1]

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ResourceDescriptor:
    id: ResourceId
    media_type: str
    size: int
    content_hash: ContentHash
    origin: OriginMetadata = ()

    def __post_init__(self) -> None:
        if not self.media_type or self.media_type.strip() != self.media_type or any(character.isspace() for character in self.media_type):
            raise ValueError("resource media type must be a non-empty token")
        if self.size < 0:
            raise ValueError("resource size must be non-negative")
        validate_content_hash(self.content_hash)
        keys = tuple(key for key, _ in self.origin)
        if tuple(sorted(keys)) != keys or len(keys) != len(set(keys)):
            raise ValueError("resource origin metadata must be sorted by unique key")


@dataclass(frozen=True, slots=True)
class Resource:
    descriptor: ResourceDescriptor
    content: bytes

    def __post_init__(self) -> None:
        if self.descriptor.size != len(self.content):
            raise ValueError("resource descriptor size does not match content")


@dataclass(frozen=True, slots=True)
class ResourceManifestEntry:
    id: ResourceId
    media_type: str | None = None
    size: int | None = None
    content_hash: ContentHash | None = None

    def __post_init__(self) -> None:
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
            raise ValueError("resource manifest ids must be unique")
        object.__setattr__(self, "entries", ordered)


def normalize_resource_id(value: str | ResourceId) -> str:
    if isinstance(value, ResourceId):
        return value.value
    if not isinstance(value, str) or value.strip() != value or not value.startswith("resource://"):
        raise ResourceIdError("resource id must be a trimmed resource:// identifier")
    if "\\" in value or "?" in value or "#" in value:
        raise ResourceIdError("resource id cannot contain host separators, query, or fragment")
    remainder = value.removeprefix("resource://")
    if "/" not in remainder:
        raise ResourceIdError("resource id requires namespace and relative path")
    namespace, path = remainder.split("/", 1)
    parts = path.split("/")
    if not namespace or any(character.isspace() for character in namespace):
        raise ResourceIdError("resource namespace must be a non-empty identifier")
    if any(not part or part in {".", ".."} or any(character.isspace() for character in part) for part in parts):
        raise ResourceIdError("resource path contains an invalid segment")
    return f"resource://{namespace}/{'/'.join(parts)}"


def resource_id(namespace: str, relative_name: str) -> ResourceId:
    if not namespace or "/" in namespace or "\\" in namespace:
        raise ResourceIdError("resource namespace must be one path segment")
    relative = relative_name.replace(chr(92), "/")
    return ResourceId(f"resource://{namespace}/{relative}")


def validate_content_hash(value: str) -> None:
    if not value.startswith(_HASH_PREFIX):
        raise ValueError("content hash must use sha256:<hex>")
    digest = value.removeprefix(_HASH_PREFIX)
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise ValueError("content hash must contain a lowercase SHA-256 digest")


__all__ = [
    "ContentHash",
    "OriginMetadata",
    "Resource",
    "ResourceDescriptor",
    "ResourceId",
    "ResourceIdError",
    "ResourceManifest",
    "ResourceManifestEntry",
    "normalize_resource_id",
    "resource_id",
    "validate_content_hash",
]
