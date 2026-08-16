from __future__ import annotations

from dataclasses import dataclass

from dryv_author.core import EventRef, OperationRef, PolicyRef, ViewRef, WorkflowRef


@dataclass(frozen=True, slots=True)
class PresentationEntryDeclaration:
    name: str
    view: ViewRef
    address: str | None = None
    navigation_parent: str | None = None
    order: int = 0
    policies: tuple[PolicyRef, ...] = ()
    operations: tuple[OperationRef[object, object], ...] = ()
    events: tuple[EventRef[object], ...] = ()
    workflows: tuple[WorkflowRef, ...] = ()


@dataclass(frozen=True, slots=True)
class PresentationDeclaration:
    channel: str
    entries: tuple[PresentationEntryDeclaration, ...] = ()


__all__ = ["PresentationDeclaration", "PresentationEntryDeclaration"]
