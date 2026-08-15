from __future__ import annotations

from dataclasses import dataclass, field

from .base import KernelData, SemanticId
from .naming import Name


@dataclass(frozen=True, slots=True)
class ValueSourceDependency:
    input: str
    source: SemanticId

    def __post_init__(self) -> None:
        if not self.input or self.input.strip() != self.input:
            raise ValueError("value source dependency input must be a non-empty trimmed string")


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
    dependencies: tuple[ValueSourceDependency, ...] = ()

    def __post_init__(self) -> None:
        if not self.output.strip():
            raise ValueError("value sources require an operation output name")
        if not self.label_fields:
            raise ValueError("value sources require at least one label field")
        if len(self.label_fields) != len(set(self.label_fields)):
            raise ValueError("value source label fields must be unique")
        if self.search_input is not None and not self.search_input.strip():
            raise ValueError("value source search_input must not be empty when provided")
        dependency_inputs = tuple(item.input for item in self.dependencies)
        if len(dependency_inputs) != len(set(dependency_inputs)):
            raise ValueError("value source dependency inputs must be unique")
        if any(item.source == self.id for item in self.dependencies):
            raise ValueError("value source cannot directly depend on itself")
