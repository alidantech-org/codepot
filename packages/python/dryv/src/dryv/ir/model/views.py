from __future__ import annotations

from dataclasses import dataclass, field

from .base import KernelData, SemanticId
from .facets import AccessFacet
from .naming import Name


@dataclass(frozen=True, slots=True)
class ViewTrigger:
    name: Name
    operation: SemanticId
    interaction: str
    payload_schema: SemanticId | None = None

    def __post_init__(self) -> None:
        if not self.interaction.strip():
            raise ValueError("view triggers require an interaction name")


@dataclass(frozen=True, slots=True)
class ViewWorkflowTrigger:
    name: Name
    workflow: SemanticId
    interaction: str
    payload_schema: SemanticId | None = None

    def __post_init__(self) -> None:
        if not self.interaction.strip():
            raise ValueError("view workflow triggers require an interaction name")


@dataclass(frozen=True, slots=True)
class ViewEventReaction:
    name: Name
    event: SemanticId
    reaction: str
    payload_schema: SemanticId | None = None

    def __post_init__(self) -> None:
        if not self.reaction.strip():
            raise ValueError("view event reactions require a reaction name")


@dataclass(frozen=True, slots=True)
class ViewConnection:
    name: Name
    target: SemanticId


@dataclass(frozen=True, slots=True)
class View:
    id: SemanticId
    name: Name
    schema: SemanticId | None = None
    parts: tuple[View, ...] = ()
    triggers: tuple[ViewTrigger, ...] = ()
    access: AccessFacet | None = None
    data: KernelData = field(default_factory=KernelData)
    schemas: tuple[SemanticId, ...] = ()
    fields: tuple[SemanticId, ...] = ()
    value_sources: tuple[SemanticId, ...] = ()
    workflow_triggers: tuple[ViewWorkflowTrigger, ...] = ()
    event_reactions: tuple[ViewEventReaction, ...] = ()
    connections: tuple[ViewConnection, ...] = ()

    def __post_init__(self) -> None:
        part_ids = tuple(item.id for item in self.parts)
        if len(part_ids) != len(set(part_ids)):
            raise ValueError("nested view ids must be unique")
        for label, values in (
            ("schema references", self.schemas),
            ("field references", self.fields),
            ("value source references", self.value_sources),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"view {label} must be unique")
        names = (
            tuple(item.name for item in self.triggers)
            + tuple(item.name for item in self.workflow_triggers)
            + tuple(item.name for item in self.event_reactions)
            + tuple(item.name for item in self.connections)
        )
        if len(names) != len(set(names)):
            raise ValueError("view interaction/reaction/connection names must be unique")


def walk_views(views: tuple[View, ...]) -> tuple[View, ...]:
    result: list[View] = []

    def visit(view: View) -> None:
        result.append(view)
        for child in view.parts:
            visit(child)

    for view in views:
        visit(view)
    return tuple(result)
