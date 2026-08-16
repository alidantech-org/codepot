from __future__ import annotations

from dataclasses import dataclass

from dryv.ir import FrozenObject

from dryv_author.core import EventRef, FailureRef, OperationRef, WorkflowRef
from dryv_author.features.operations import OperationInput, OperationOutputSpec


@dataclass(frozen=True, slots=True)
class CompensationDeclaration:
    operation: OperationRef[object, object]
    input_bindings: FrozenObject = ()
    condition: str | None = None
    retry_attempts: int = 0
    continue_on_failure: bool = False


@dataclass(frozen=True, slots=True)
class DecisionCaseDeclaration:
    condition: str
    target: str


@dataclass(frozen=True, slots=True)
class WorkflowStepDeclaration:
    name: str
    kind: str
    operation: OperationRef[object, object] | None = None
    workflow: WorkflowRef | None = None
    compensation: CompensationDeclaration | None = None
    nested_steps: tuple[WorkflowStepDeclaration, ...] = ()
    decision_cases: tuple[DecisionCaseDeclaration, ...] = ()
    wait_event: EventRef[object] | None = None
    timeout_seconds: int | None = None


@dataclass(frozen=True, slots=True)
class WorkflowTransitionDeclaration:
    source: str
    target: str
    condition: str | None = None


@dataclass(frozen=True, slots=True)
class WorkflowDeclaration:
    inputs: tuple[OperationInput, ...] = ()
    outputs: tuple[OperationOutputSpec, ...] = ()
    steps: tuple[WorkflowStepDeclaration, ...] = ()
    transitions: tuple[WorkflowTransitionDeclaration, ...] = ()
    failures: tuple[FailureRef, ...] = ()
    emitted_events: tuple[EventRef[object], ...] = ()
    compensation_order: str = "reverse_completed"
    continue_compensation_on_failure: bool = True
    durable: bool = False
    timeout_seconds: int | None = None


__all__ = ["CompensationDeclaration", "DecisionCaseDeclaration", "WorkflowDeclaration", "WorkflowStepDeclaration", "WorkflowTransitionDeclaration"]
