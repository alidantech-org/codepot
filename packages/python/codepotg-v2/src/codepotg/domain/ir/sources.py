from __future__ import annotations

from dataclasses import dataclass, field

from .base import KernelData, SemanticId
from .naming import Name


@dataclass(frozen=True, slots=True)
class ValueSource:
    """Neutral description of how a selectable value collection is obtained."""

    id: SemanticId
    name: Name
    operation: SemanticId
    output: str
    value_field: SemanticId
    label_fields: tuple[SemanticId, ...]
    search_input: str | None = None
    data: KernelData = field(default_factory=KernelData)

    def __post_init__(self) -> None:
        if not self.output:
            raise ValueError("value sources require an operation output name")
        if not self.label_fields:
            raise ValueError("value sources require at least one label field")
        if len(self.label_fields) != len(set(self.label_fields)):
            raise ValueError("value source label fields must be unique")
