from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from .base import FrozenObject, KernelData, SemanticId, validate_frozen_object
from .events import OperationEffects
from .facets import WorkflowFacets
from .naming import Name
from .operations import OperationFailure, OperationOutput
from .schemas import SchemaUse


class WorkflowStepKind(StrEnum):
    OPERATION = "operation"
    DECISION = "decision"
    PARALLEL = "parallel"
    WAIT = "wait"
    END = "end"


@dataclass(frozen=True, slots=True)
class Compensation:
    operation: SemanticId
    input_bindings: FrozenObject = ()
    condition: str | None = None
    retry_attempts: int = 0
    continue_on_failure: bool = False

    def __post_init__(self) -> None:
        if self.retry_attempts < 0:
            raise ValueError("compensation retry_attempts must be non-negative")
        validate_frozen_object("compensation input bindings", self.input_bindings)


@dataclass(frozen=True, slots=True)
class WorkflowDecisionCase:
    condition: str
    target: str


@dataclass(frozen=True, slots=True)
class WorkflowStep:
    name: str
    kind: WorkflowStepKind
    operation: SemanticId | None = None
    compensation: Compensation | None = None
    nested_steps: tuple[WorkflowStep, ...] = ()
    decision_cases: tuple[WorkflowDecisionCase, ...] = ()
    wait_event: SemanticId | None = None
    timeout_seconds: int | None = None
    data: KernelData = field(default_factory=KernelData)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("workflow steps require a name")
        if self.kind is WorkflowStepKind.OPERATION and self.operation is None:
            raise ValueError("operation steps require an operation")
        if self.kind is WorkflowStepKind.PARALLEL and not self.nested_steps:
            raise ValueError("parallel steps require nested steps")
        if self.kind is WorkflowStepKind.DECISION and not self.decision_cases:
            raise ValueError("decision steps require cases")
        if self.kind is WorkflowStepKind.WAIT and self.wait_event is None:
            raise ValueError("wait steps require an event")
        if self.timeout_seconds is not None and self.timeout_seconds < 1:
            raise ValueError("workflow step timeouts must be positive")


@dataclass(frozen=True, slots=True)
class WorkflowTransition:
    source: str
    target: str
    condition: str | None = None


@dataclass(frozen=True, slots=True)
class Workflow:
    id: SemanticId
    name: Name
    inputs: tuple[SchemaUse, ...] = ()
    outputs: tuple[OperationOutput, ...] = ()
    steps: tuple[WorkflowStep, ...] = ()
    transitions: tuple[WorkflowTransition, ...] = ()
    failures: tuple[OperationFailure, ...] = ()
    effects: OperationEffects = field(default_factory=OperationEffects)
    facets: WorkflowFacets = field(default_factory=WorkflowFacets)
    compensation_order: str = "reverse_completed"
    continue_compensation_on_failure: bool = True
    data: KernelData = field(default_factory=KernelData)

    def __post_init__(self) -> None:
        names = tuple(step.name for step in self.steps)
        if len(names) != len(set(names)):
            raise ValueError("workflow step names must be unique")
        if self.compensation_order not in {"reverse_completed", "declared"}:
            raise ValueError("unsupported workflow compensation order")


def walk_workflow_steps(steps: tuple[WorkflowStep, ...]) -> tuple[WorkflowStep, ...]:
    result: list[WorkflowStep] = []

    def visit(step: WorkflowStep) -> None:
        result.append(step)
        for child in step.nested_steps:
            visit(child)

    for step in steps:
        visit(step)
    return tuple(result)
