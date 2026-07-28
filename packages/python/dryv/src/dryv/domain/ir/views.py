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
        if not self.interaction:
            raise ValueError("view triggers require an interaction name")


@dataclass(frozen=True, slots=True)
class View:
    id: SemanticId
    name: Name
    schema: SemanticId | None = None
    parts: tuple[View, ...] = ()
    triggers: tuple[ViewTrigger, ...] = ()
    access: AccessFacet | None = None
    data: KernelData = field(default_factory=KernelData)

    def __post_init__(self) -> None:
        part_ids = tuple(item.id for item in self.parts)
        if len(part_ids) != len(set(part_ids)):
            raise ValueError("nested view ids must be unique")


def walk_views(views: tuple[View, ...]) -> tuple[View, ...]:
    result: list[View] = []

    def visit(view: View) -> None:
        result.append(view)
        for child in view.parts:
            visit(child)

    for view in views:
        visit(view)
    return tuple(result)
