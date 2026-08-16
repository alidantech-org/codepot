"""Bounded logical resource identity and content verification."""

from .contracts import (
    ContentHash,
    OriginMetadata,
    Resource,
    ResourceDescriptor,
    ResourceId,
    ResourceIdError,
    ResourceManifest,
    ResourceManifestEntry,
    normalize_resource_id,
    resource_id,
    validate_content_hash,
)
from .registry import ResourceError, ResourceRegistry

__all__ = [
    "ContentHash",
    "OriginMetadata",
    "Resource",
    "ResourceDescriptor",
    "ResourceError",
    "ResourceId",
    "ResourceIdError",
    "ResourceManifest",
    "ResourceManifestEntry",
    "ResourceRegistry",
    "normalize_resource_id",
    "resource_id",
    "validate_content_hash",
]
