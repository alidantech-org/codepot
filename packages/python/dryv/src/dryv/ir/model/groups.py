from __future__ import annotations

from dataclasses import dataclass, field

from .base import KernelData, SemanticId
from .events import Event
from .facets import GroupFacets
from .naming import Name
from .operations import Operation
from .policies import Policy
from .presentations import Presentation
from .schemas import Schema
from .sources import ValueSource
from .storage import StorageMapping, StorageNamespace
from .views import View
from .workflows import Workflow


@dataclass(frozen=True, slots=True)
class Group:
    id: SemanticId
    name: Name
    path: tuple[str, ...] = ()
    schemas: tuple[Schema, ...] = ()
    operations: tuple[Operation, ...] = ()
    views: tuple[View, ...] = ()
    storage_mappings: tuple[StorageMapping, ...] = ()
    workflows: tuple[Workflow, ...] = ()
    policies: tuple[Policy, ...] = ()
    events: tuple[Event, ...] = ()
    groups: tuple[Group, ...] = ()
    facets: GroupFacets = field(default_factory=GroupFacets)
    data: KernelData = field(default_factory=KernelData)
    value_sources: tuple[ValueSource, ...] = ()

    def __post_init__(self) -> None:
        if any(not part or "/" in part or "\\" in part for part in self.path):
            raise ValueError("group path parts must be non-empty path segments")
        child_ids = tuple(item.id for item in self.groups)
        if len(child_ids) != len(set(child_ids)):
            raise ValueError("nested group ids must be unique")
        source_ids = tuple(item.id for item in self.value_sources)
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("group value source ids must be unique")

    @property
    def storage(self) -> StorageNamespace:
        return StorageNamespace(self.storage_mappings)


@dataclass(frozen=True, slots=True)
class Contract:
    id: SemanticId
    name: Name
    groups: tuple[Group, ...]
    version: str | None = None
    data: KernelData = field(default_factory=KernelData)
    presentations: tuple[Presentation, ...] = ()

    def __post_init__(self) -> None:
        if not self.groups:
            raise ValueError("contracts require at least one group")
        group_ids = tuple(item.id for item in self.groups)
        if len(group_ids) != len(set(group_ids)):
            raise ValueError("contract group ids must be unique")
        presentation_ids = tuple(item.id for item in self.presentations)
        if len(presentation_ids) != len(set(presentation_ids)):
            raise ValueError("contract presentation ids must be unique")


def walk_groups(groups: tuple[Group, ...]) -> tuple[Group, ...]:
    result: list[Group] = []

    def visit(group: Group) -> None:
        result.append(group)
        for child in group.groups:
            visit(child)

    for group in groups:
        visit(group)
    return tuple(result)
