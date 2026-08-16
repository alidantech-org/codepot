from __future__ import annotations

from dataclasses import dataclass

from dryv_author.core import EventRef, FieldRef, OperationRef, SchemaRef, ValueSourceRef, ViewRef, WorkflowRef


@dataclass(frozen=True, slots=True)
class ViewTriggerDeclaration:
    name: str
    operation: OperationRef[object, object]
    interaction: str
    payload_schema: SchemaRef[object] | None = None


@dataclass(frozen=True, slots=True)
class ViewWorkflowTriggerDeclaration:
    name: str
    workflow: WorkflowRef
    interaction: str
    payload_schema: SchemaRef[object] | None = None


@dataclass(frozen=True, slots=True)
class ViewEventReactionDeclaration:
    name: str
    event: EventRef[object]
    reaction: str
    payload_schema: SchemaRef[object] | None = None


@dataclass(frozen=True, slots=True)
class ViewConnectionDeclaration:
    name: str
    target: ViewRef


@dataclass(frozen=True, slots=True)
class ViewDeclaration:
    schema: SchemaRef[object] | None = None
    schemas: tuple[SchemaRef[object], ...] = ()
    fields: tuple[FieldRef[object], ...] = ()
    value_sources: tuple[ValueSourceRef[object], ...] = ()
    triggers: tuple[ViewTriggerDeclaration, ...] = ()
    workflow_triggers: tuple[ViewWorkflowTriggerDeclaration, ...] = ()
    event_reactions: tuple[ViewEventReactionDeclaration, ...] = ()
    connections: tuple[ViewConnectionDeclaration, ...] = ()


__all__ = ["ViewConnectionDeclaration", "ViewDeclaration", "ViewEventReactionDeclaration", "ViewTriggerDeclaration", "ViewWorkflowTriggerDeclaration"]
