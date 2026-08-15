"""Portable logical resources supplied to Dryv Engine.

The Resources Feature owns logical identity, content verification, bounded
streaming, manifests, and content-addressed reuse. Resource acquisition from
local files or private Git repositories belongs to Project Clients.
"""

from .ids import ResourceId, ResourceIdError, normalize_resource_id, resource_id
from .models import (
    ContentHash,
    OriginMetadata,
    Resource,
    ResourceDescriptor,
    ResourceManifest,
    ResourceManifestEntry,
    validate_content_hash,
)
from .registry import ResourceError, ResourceRegistry

__all__ = ["ContentHash", "OriginMetadata", "Resource", "ResourceDescriptor", "ResourceError", "ResourceId", "ResourceIdError", "ResourceManifest", "ResourceManifestEntry", "ResourceRegistry", "normalize_resource_id", "resource_id", "validate_content_hash"]
