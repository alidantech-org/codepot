from __future__ import annotations

from dataclasses import dataclass, field

from .base import KernelData, SemanticId
from .events import OperationEffects
from .facets import OperationFacets
from .naming import Name
from .schemas import SchemaUse


@dataclass(frozen=True, slots=True)
class OperationOutput:
    name: Name | None = None
    schema: SemanticId | None = None
    optional: bool = False
    data: KernelData = field(default_factory=KernelData)


@dataclass(frozen=True, slots=True)
class OperationRelations:
    """Typed forward Operation relationships with neutral software meaning."""

    invokes: tuple[SemanticId, ...] = ()
    requires: tuple[SemanticId, ...] = ()
    delegates_to: tuple[SemanticId, ...] = ()
    before: tuple[SemanticId, ...] = ()
    after: tuple[SemanticId, ...] = ()
    triggers_workflows: tuple[SemanticId, ...] = ()

    def __post_init__(self) -> None:
        for label, values in (
            ("invoked operations", self.invokes),
            ("required operations", self.requires),
            ("delegated operations", self.delegates_to),
            ("before operations", self.before),
            ("after operations", self.after),
            ("triggered workflows", self.triggers_workflows),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"{label} must be unique")


@dataclass(frozen=True, slots=True)
class Operation:
    id: SemanticId
    name: Name
    inputs: tuple[SchemaUse, ...] = ()
    outputs: tuple[OperationOutput, ...] = ()
    failures: tuple[SemanticId, ...] = ()
    effects: OperationEffects = field(default_factory=OperationEffects)
    facets: OperationFacets = field(default_factory=OperationFacets)
    data: KernelData = field(default_factory=KernelData)
    subjects: tuple[SemanticId, ...] = ()
    policies: tuple[SemanticId, ...] = ()
    relations: OperationRelations = field(default_factory=OperationRelations)

    def __post_init__(self) -> None:
        input_names = tuple(item.name.raw.original for item in self.inputs)
        if len(input_names) != len(set(input_names)):
            raise ValueError("operation input names must be unique")
        output_names = tuple(item.name.raw.original for item in self.outputs if item.name is not None)
        if len(output_names) != len(set(output_names)):
            raise ValueError("named operation outputs must be unique")
        for label, values in (
            ("failure references", self.failures),
            ("subject schema references", self.subjects),
            ("policy references", self.policies),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"operation {label} must be unique")
        for label, values in (
            ("required operations", self.relations.requires),
            ("delegated operations", self.relations.delegates_to),
            ("before operations", self.relations.before),
            ("after operations", self.relations.after),
        ):
            if self.id in values:
                raise ValueError(f"operation cannot reference itself in {label}")
