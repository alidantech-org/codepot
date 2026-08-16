from __future__ import annotations

from dataclasses import dataclass, field

from .base import KernelData, SemanticId
from .events import Event
from .facets import GroupFacets
from .failures import Failure
from .naming import Name
from .operations import Operation
from .policies import Policy
from .presentations import Presentation
from .properties import Property
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
    properties: tuple[Property, ...] = ()
    schemas: tuple[Schema, ...] = ()
    operations: tuple[Operation, ...] = ()
    views: tuple[View, ...] = ()
    storage_mappings: tuple[StorageMapping, ...] = ()
    policies: tuple[Policy, ...] = ()
    failures: tuple[Failure, ...] = ()
    events: tuple[Event, ...] = ()
    groups: tuple[Group, ...] = ()
    facets: GroupFacets = field(default_factory=GroupFacets)
    data: KernelData = field(default_factory=KernelData)
    value_sources: tuple[ValueSource, ...] = ()

    def __post_init__(self) -> None:
        if any(not part or "/" in part or "\\" in part for part in self.path):
            raise ValueError("group path parts must be non-empty path segments")
        for label, items in (
            ("nested group", self.groups),
            ("property", self.properties),
            ("failure", self.failures),
            ("value source", self.value_sources),
        ):
            ids = tuple(item.id for item in items)
            if len(ids) != len(set(ids)):
                raise ValueError(f"group {label} ids must be unique")

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
    workflows: tuple[Workflow, ...] = ()

    def __post_init__(self) -> None:
        if not self.groups:
            raise ValueError("contracts require at least one group")
        group_ids = tuple(item.id for item in self.groups)
        if len(group_ids) != len(set(group_ids)):
            raise ValueError("contract group ids must be unique")
        workflow_ids = tuple(item.id for item in self.workflows)
        if len(workflow_ids) != len(set(workflow_ids)):
            raise ValueError("contract workflow ids must be unique")
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
