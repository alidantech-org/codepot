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
class OperationFailure:
    code: str
    schema: SemanticId | None = None
    message: str | None = None
    data: KernelData = field(default_factory=KernelData)

    def __post_init__(self) -> None:
        if not self.code:
            raise ValueError("operation failure code must not be empty")


@dataclass(frozen=True, slots=True)
class Operation:
    id: SemanticId
    name: Name
    inputs: tuple[SchemaUse, ...] = ()
    outputs: tuple[OperationOutput, ...] = ()
    failures: tuple[OperationFailure, ...] = ()
    effects: OperationEffects = field(default_factory=OperationEffects)
    facets: OperationFacets = field(default_factory=OperationFacets)
    data: KernelData = field(default_factory=KernelData)

    def __post_init__(self) -> None:
        input_names = tuple(item.name.raw.original for item in self.inputs)
        if len(input_names) != len(set(input_names)):
            raise ValueError("operation input names must be unique")
        failure_codes = tuple(item.code for item in self.failures)
        if len(failure_codes) != len(set(failure_codes)):
            raise ValueError("operation failure codes must be unique")
