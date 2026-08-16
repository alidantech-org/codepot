from __future__ import annotations

from dataclasses import dataclass

from dryv_author.core import EventRef, FailureRef, OperationRef, PolicyRef, SchemaRef, WorkflowRef


@dataclass(frozen=True, slots=True)
class OperationInput:
    name: str
    schema: SchemaRef[object]
    required: bool = False
    nullable: bool = False
    readonly: bool = False


@dataclass(frozen=True, slots=True)
class OperationOutputSpec:
    schema: SchemaRef[object] | None = None
    name: str | None = None
    optional: bool = False


@dataclass(frozen=True, slots=True)
class OperationEventEffect:
    event: EventRef[object]
    payload_schema: SchemaRef[object] | None = None
    condition: str | None = None


@dataclass(frozen=True, slots=True)
class OperationRelationsDeclaration:
    invokes: tuple[OperationRef[object, object], ...] = ()
    requires: tuple[OperationRef[object, object], ...] = ()
    delegates_to: tuple[OperationRef[object, object], ...] = ()
    before: tuple[OperationRef[object, object], ...] = ()
    after: tuple[OperationRef[object, object], ...] = ()
    triggers_workflows: tuple[WorkflowRef, ...] = ()


@dataclass(frozen=True, slots=True)
class OperationDeclaration:
    inputs: tuple[OperationInput, ...] = ()
    outputs: tuple[OperationOutputSpec, ...] = ()
    failures: tuple[FailureRef, ...] = ()
    events: tuple[OperationEventEffect, ...] = ()
    http_method: str | None = None
    http_path: str | None = None
    operation_id: str | None = None
    policies: tuple[PolicyRef, ...] = ()
    subjects: tuple[SchemaRef[object], ...] = ()
    relations: OperationRelationsDeclaration = OperationRelationsDeclaration()

    def __post_init__(self) -> None:
        input_names = tuple(item.name for item in self.inputs)
        if len(input_names) != len(set(input_names)):
            raise ValueError("operation input names must be unique")
        output_names = tuple(item.name for item in self.outputs if item.name is not None)
        if len(output_names) != len(set(output_names)):
            raise ValueError("named operation outputs must be unique")
        if (self.http_method is None) != (self.http_path is None):
            raise ValueError("HTTP method and path must be supplied together")


__all__ = ["OperationDeclaration", "OperationEventEffect", "OperationInput", "OperationOutputSpec", "OperationRelationsDeclaration"]
