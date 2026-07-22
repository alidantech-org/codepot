"""Owner folder lookup helpers."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.spec.ir.resource.definition import ResourceDefinition
from archives.codepot.src.spec.ir.schema.entity.definition import EntityDefinition
from archives.codepot.src.spec.utils.enums import SpecSubject


@dataclass(frozen=True)
class OwnerFolderInfo:
    """Resolved owner folder metadata."""

    key: str
    subject: SpecSubject
    folders: tuple[str, ...]


@dataclass(frozen=True)
class OwnerFolderIndex:
    """Typed owner folder lookup index."""

    resources: dict[str, OwnerFolderInfo]
    entities: dict[str, OwnerFolderInfo]

    def find(
        self,
        *,
        subject: SpecSubject,
        key: str,
    ) -> OwnerFolderInfo | None:
        """Find owner folder info by subject/key."""

        if subject == SpecSubject.RESOURCES:
            return self.resources.get(key)

        if subject == SpecSubject.ENTITIES:
            return self.entities.get(key)

        return None


def _resource_folder_info(
    key: str,
    resource: ResourceDefinition,
) -> OwnerFolderInfo:
    """Create folder info for a resource."""

    return OwnerFolderInfo(
        key=key,
        subject=SpecSubject.RESOURCES,
        folders=tuple(resource.folders),
    )


def _entity_folder_info(
    key: str,
    entity: EntityDefinition,
) -> OwnerFolderInfo:
    """Create folder info for an entity.

    Entity folders must represent parent/container folders only.
    Do not fallback to the entity name because owner.name.path already exposes
    the leaf folder.
    """

    return OwnerFolderInfo(
        key=key,
        subject=SpecSubject.ENTITIES,
        folders=(),
    )


def build_owner_folder_index(
    *,
    resources: dict[str, ResourceDefinition],
    entities: dict[str, EntityDefinition],
) -> OwnerFolderIndex:
    """Build typed owner folder index from typed IR document sections."""

    return OwnerFolderIndex(
        resources={
            key: _resource_folder_info(key, resource)
            for key, resource in resources.items()
        },
        entities={
            key: _entity_folder_info(key, entity)
            for key, entity in entities.items()
        },
    )
