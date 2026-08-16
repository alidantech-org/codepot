from __future__ import annotations

from dataclasses import dataclass

from dryv_author.refs import EventRef, OperationRef, SchemaRef


@dataclass(frozen=True, slots=True)
class SchemaUseDeclaration:
    name: str
    schema: SchemaRef[object]
    required: bool = False
    nullable: bool = False
    readonly: bool = False


@dataclass(frozen=True, slots=True)
class OperationOutputDeclaration:
    schema: SchemaRef[object] | None = None
    name: str | None = None
    optional: bool = False


@dataclass(frozen=True, slots=True)
class OperationFailureDeclaration:
    code: str
    schema: SchemaRef[object] | None = None
    message: str | None = None


@dataclass(frozen=True, slots=True)
class OperationDeclaration:
    inputs: tuple[SchemaUseDeclaration, ...] = ()
    outputs: tuple[OperationOutputDeclaration, ...] = ()
    failures: tuple[OperationFailureDeclaration, ...] = ()
    emitted_events: tuple[EventRef[object], ...] = ()
    http_method: str | None = None
    http_path: str | None = None
    operation_id: str | None = None

    def __post_init__(self) -> None:
        input_names = tuple(item.name for item in self.inputs)
        if len(input_names) != len(set(input_names)):
            raise ValueError("operation input names must be unique")
        failure_codes = tuple(item.code for item in self.failures)
        if len(failure_codes) != len(set(failure_codes)):
            raise ValueError("operation failure codes must be unique")
        if (self.http_method is None) != (self.http_path is None):
            raise ValueError("HTTP method and path must be supplied together")
        if self.http_method is not None:
            method = self.http_method.upper()
            if method not in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}:
                raise ValueError(f"unsupported HTTP method: {self.http_method}")
            object.__setattr__(self, "http_method", method)
        if self.http_path is not None and not self.http_path.startswith("/"):
            raise ValueError("HTTP paths must start with /")


@dataclass(frozen=True, slots=True)
class EventDeclaration:
    payload_schema: SchemaRef[object] | None = None
    context_schema: SchemaRef[object] | None = None
    version: str | None = None
    source: str | None = None


@dataclass(frozen=True, slots=True)
class PolicyDeclaration:
    roles: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    scopes: tuple[str, ...] = ()
    ownership: str | None = None
    conditions: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class StorageFieldDeclaration:
    field_name: str
    column: str
    column_type: str | None = None
    indexed: bool = False
    unique: bool = False
    nullable: bool | None = None


@dataclass(frozen=True, slots=True)
class StorageDeclaration:
    schema: SchemaRef[object]
    source: str
    fields: tuple[StorageFieldDeclaration, ...] = ()
    primary_key: tuple[str, ...] = ()
    indexes: tuple[tuple[str, ...], ...] = ()

    def __post_init__(self) -> None:
        if not self.source:
            raise ValueError("storage source must not be empty")
        names = tuple(item.field_name for item in self.fields)
        if len(names) != len(set(names)):
            raise ValueError("storage mapped fields must be unique")
        if len(self.primary_key) != len(set(self.primary_key)):
            raise ValueError("storage primary-key fields must be unique")


@dataclass(frozen=True, slots=True)
class ViewTriggerDeclaration:
    name: str
    operation: OperationRef[object, object]
    interaction: str
    payload_schema: SchemaRef[object] | None = None


@dataclass(frozen=True, slots=True)
class ViewDeclaration:
    schema: SchemaRef[object] | None = None
    triggers: tuple[ViewTriggerDeclaration, ...] = ()


@dataclass(frozen=True, slots=True)
class WorkflowStepDeclaration:
    name: str
    kind: str
    operation: OperationRef[object, object] | None = None
    wait_event: EventRef[object] | None = None
    timeout_seconds: int | None = None
    decision_cases: tuple[tuple[str, str], ...] = ()
    nested_steps: tuple[WorkflowStepDeclaration, ...] = ()

    def __post_init__(self) -> None:
        if self.kind not in {"operation", "decision", "parallel", "wait", "end"}:
            raise ValueError(f"unsupported workflow step kind: {self.kind}")
        if self.kind == "operation" and self.operation is None:
            raise ValueError("operation workflow steps require an operation")
        if self.kind == "wait" and self.wait_event is None:
            raise ValueError("wait workflow steps require an event")
        if self.kind == "parallel" and not self.nested_steps:
            raise ValueError("parallel workflow steps require nested steps")
        if self.kind == "decision" and not self.decision_cases:
            raise ValueError("decision workflow steps require decision cases")
        if self.timeout_seconds is not None and self.timeout_seconds < 1:
            raise ValueError("workflow step timeout must be positive")


@dataclass(frozen=True, slots=True)
class WorkflowDeclaration:
    inputs: tuple[SchemaUseDeclaration, ...] = ()
    outputs: tuple[OperationOutputDeclaration, ...] = ()
    steps: tuple[WorkflowStepDeclaration, ...] = ()
    transitions: tuple[tuple[str, str, str | None], ...] = ()
    failures: tuple[OperationFailureDeclaration, ...] = ()
    emitted_events: tuple[EventRef[object], ...] = ()
    compensation_order: str = "reverse_completed"
    continue_compensation_on_failure: bool = True

    def __post_init__(self) -> None:
        names = tuple(item.name for item in self.steps)
        if len(names) != len(set(names)):
            raise ValueError("workflow step names must be unique")
        if self.compensation_order not in {"reverse_completed", "declared"}:
            raise ValueError("unsupported workflow compensation order")
