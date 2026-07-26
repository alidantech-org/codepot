from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import TypeAlias

from .core import SourceSpan
from .naming import Name

JsonScalar: TypeAlias = str | int | float | bool | None
FrozenValue: TypeAlias = JsonScalar | tuple["FrozenValue", ...] | tuple[tuple[str, "FrozenValue"], ...]
FrozenObject: TypeAlias = tuple[tuple[str, FrozenValue], ...]

_SEMANTIC_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")


@dataclass(frozen=True, slots=True, order=True)
class SemanticId:
    value: str

    def __post_init__(self) -> None:
        if not _SEMANTIC_ID.fullmatch(self.value):
            raise ValueError(f"invalid semantic id: {self.value!r}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Documentation:
    summary: str | None = None
    description: str | None = None
    external_url: str | None = None


@dataclass(frozen=True, slots=True)
class Provenance:
    source_kind: str
    source_id: str
    pointer: str | None = None
    span: SourceSpan | None = None

    def __post_init__(self) -> None:
        if not self.source_kind or not self.source_id:
            raise ValueError("provenance requires source_kind and source_id")


@dataclass(frozen=True, slots=True)
class KernelData:
    documentation: Documentation = field(default_factory=Documentation)
    provenance: Provenance | None = None
    extensions: FrozenObject = ()
    raw: FrozenObject = ()

    def __post_init__(self) -> None:
        _validate_frozen_object("extensions", self.extensions)
        _validate_frozen_object("raw", self.raw)


class SchemaKind(str, Enum):
    PRIMITIVE = "primitive"
    LITERAL = "literal"
    ENUM = "enum"
    OBJECT = "object"
    ARRAY = "array"
    MAP = "map"
    TUPLE = "tuple"
    UNION = "union"
    INTERSECTION = "intersection"
    ALIAS = "alias"
    UNKNOWN = "unknown"


class TypeKind(str, Enum):
    PRIMITIVE = "primitive"
    REFERENCE = "reference"
    LITERAL = "literal"
    ARRAY = "array"
    MAP = "map"
    TUPLE = "tuple"
    UNION = "union"
    INTERSECTION = "intersection"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class TypeExpression:
    kind: TypeKind
    name: str | None = None
    reference: SemanticId | None = None
    arguments: tuple[TypeExpression, ...] = ()
    literal: JsonScalar = None

    def __post_init__(self) -> None:
        if self.kind is TypeKind.PRIMITIVE and not self.name:
            raise ValueError("primitive type expressions require a name")
        if self.kind is TypeKind.REFERENCE and self.reference is None:
            raise ValueError("reference type expressions require a semantic id")
        if self.kind is TypeKind.ARRAY and len(self.arguments) != 1:
            raise ValueError("array type expressions require exactly one item type")
        if self.kind is TypeKind.MAP and len(self.arguments) != 2:
            raise ValueError("map type expressions require key and value types")
        if self.kind in {TypeKind.UNION, TypeKind.INTERSECTION} and len(self.arguments) < 2:
            raise ValueError(f"{self.kind.value} requires at least two members")
        if self.kind in {TypeKind.TUPLE} and not self.arguments:
            raise ValueError("tuple type expressions require at least one member")

    @classmethod
    def primitive(cls, name: str) -> TypeExpression:
        return cls(TypeKind.PRIMITIVE, name=name)

    @classmethod
    def reference_to(cls, semantic_id: SemanticId | str) -> TypeExpression:
        return cls(TypeKind.REFERENCE, reference=_semantic_id(semantic_id))

    @classmethod
    def literal_value(cls, value: JsonScalar) -> TypeExpression:
        return cls(TypeKind.LITERAL, literal=value)

    @classmethod
    def array_of(cls, item: TypeExpression) -> TypeExpression:
        return cls(TypeKind.ARRAY, arguments=(item,))

    @classmethod
    def map_of(cls, key: TypeExpression, value: TypeExpression) -> TypeExpression:
        return cls(TypeKind.MAP, arguments=(key, value))

    @classmethod
    def tuple_of(cls, *members: TypeExpression) -> TypeExpression:
        return cls(TypeKind.TUPLE, arguments=members)

    @classmethod
    def union_of(cls, *members: TypeExpression) -> TypeExpression:
        return cls(TypeKind.UNION, arguments=members)

    @classmethod
    def intersection_of(cls, *members: TypeExpression) -> TypeExpression:
        return cls(TypeKind.INTERSECTION, arguments=members)


@dataclass(frozen=True, slots=True)
class FieldConstraints:
    minimum: int | float | None = None
    maximum: int | float | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    format: str | None = None
    origins: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise ValueError("minimum must not exceed maximum")
        if self.min_length is not None and self.min_length < 0:
            raise ValueError("min_length must be non-negative")
        if self.max_length is not None and self.max_length < 0:
            raise ValueError("max_length must be non-negative")
        if (
            self.min_length is not None
            and self.max_length is not None
            and self.min_length > self.max_length
        ):
            raise ValueError("min_length must not exceed max_length")
        _validate_pairs("constraint origins", self.origins)


@dataclass(frozen=True, slots=True)
class SchemaField:
    id: SemanticId
    name: Name
    type: TypeExpression
    required: bool = False
    nullable: bool = False
    readonly: bool = False
    constraints: FieldConstraints = field(default_factory=FieldConstraints)
    data: KernelData = field(default_factory=KernelData)


@dataclass(frozen=True, slots=True)
class Schema:
    id: SemanticId
    name: Name
    kind: SchemaKind
    fields: tuple[SchemaField, ...] = ()
    enum_values: tuple[str, ...] = ()
    item_type: TypeExpression | None = None
    alias_of: TypeExpression | None = None
    literal: JsonScalar = None
    data: KernelData = field(default_factory=KernelData)

    def __post_init__(self) -> None:
        _validate_unique_ids("schema fields", (item.id for item in self.fields))
        if self.kind is SchemaKind.OBJECT and self.enum_values:
            raise ValueError("object schemas cannot declare enum values")
        if self.kind is SchemaKind.ENUM and not self.enum_values:
            raise ValueError("enum schemas require at least one value")
        if self.kind is SchemaKind.ARRAY and self.item_type is None:
            raise ValueError("array schemas require item_type")
        if self.kind is SchemaKind.ALIAS and self.alias_of is None:
            raise ValueError("alias schemas require alias_of")


@dataclass(frozen=True, slots=True)
class SchemaUse:
    name: Name
    schema: SemanticId
    required: bool = False
    nullable: bool = False
    readonly: bool = False
    data: KernelData = field(default_factory=KernelData)


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
class EventEffect:
    event: SemanticId
    payload_schema: SemanticId | None = None
    condition: str | None = None


@dataclass(frozen=True, slots=True)
class OperationEffects:
    events: tuple[EventEffect, ...] = ()


@dataclass(frozen=True, slots=True)
class HttpFacet:
    method: str
    path: str
    operation_id: str | None = None

    def __post_init__(self) -> None:
        normalized = self.method.upper()
        if not normalized or not self.path.startswith("/"):
            raise ValueError("HTTP facets require a method and absolute route path")
        object.__setattr__(self, "method", normalized)


@dataclass(frozen=True, slots=True)
class AccessFacet:
    uses: tuple[SemanticId, ...] = ()
    inherited: tuple[SemanticId, ...] = ()
    effective: tuple[SemanticId, ...] = ()
    public: bool = False
    authenticated: bool = False

    def __post_init__(self) -> None:
        if self.public and self.authenticated:
            raise ValueError("access cannot be both public and authenticated")
        _validate_unique_ids("access policies", self.uses + self.inherited + self.effective)


class TriggerKind(str, Enum):
    EVENT = "event"
    SCHEDULE = "schedule"
    HTTP = "http"
    INTERACTION = "interaction"
    STORAGE = "storage"
    SYSTEM = "system"


@dataclass(frozen=True, slots=True)
class TriggerFacet:
    kind: TriggerKind
    event: SemanticId | None = None
    expression: str | None = None
    method: str | None = None
    path: str | None = None
    view: SemanticId | None = None
    interaction: str | None = None
    storage: SemanticId | None = None
    signal: str | None = None

    def __post_init__(self) -> None:
        required = {
            TriggerKind.EVENT: self.event is not None,
            TriggerKind.SCHEDULE: bool(self.expression),
            TriggerKind.HTTP: bool(self.method and self.path),
            TriggerKind.INTERACTION: self.view is not None and bool(self.interaction),
            TriggerKind.STORAGE: self.storage is not None,
            TriggerKind.SYSTEM: bool(self.signal),
        }
        if not required[self.kind]:
            raise ValueError(f"trigger {self.kind.value} is missing its required data")


class ExecutionPhase(str, Enum):
    BEFORE = "before"
    AROUND = "around"
    AFTER_SUCCESS = "after_success"
    AFTER_FAILURE = "after_failure"
    AFTER_COMPLETE = "after_complete"


@dataclass(frozen=True, slots=True)
class ExecutionHook:
    phase: ExecutionPhase
    operation: SemanticId
    order: int = 0
    condition: str | None = None
    can_stop: bool = False


@dataclass(frozen=True, slots=True)
class ExecutionFacet:
    hooks: tuple[ExecutionHook, ...] = ()


@dataclass(frozen=True, slots=True)
class EventsFacet:
    consumes: tuple[SemanticId, ...] = ()
    channels: tuple[str, ...] = ()
    bindings: FrozenObject = ()

    def __post_init__(self) -> None:
        _validate_unique_ids("consumed events", self.consumes)
        _validate_frozen_object("event bindings", self.bindings)


@dataclass(frozen=True, slots=True)
class OperationFacets:
    http: HttpFacet | None = None
    access: AccessFacet | None = None
    trigger: TriggerFacet | None = None
    execution: ExecutionFacet | None = None
    events: EventsFacet | None = None


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
        names = tuple(item.name.raw.original for item in self.inputs)
        if len(names) != len(set(names)):
            raise ValueError("operation input names must be unique")
        codes = tuple(item.code for item in self.failures)
        if len(codes) != len(set(codes)):
            raise ValueError("operation failure codes must be unique")


@dataclass(frozen=True, slots=True)
class Policy:
    id: SemanticId
    name: Name
    roles: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    scopes: tuple[str, ...] = ()
    ownership: str | None = None
    conditions: tuple[str, ...] = ()
    data: KernelData = field(default_factory=KernelData)


@dataclass(frozen=True, slots=True)
class Event:
    id: SemanticId
    name: Name
    payload_schema: SemanticId | None = None
    context_schema: SemanticId | None = None
    version: str | None = None
    source: str | None = None
    data: KernelData = field(default_factory=KernelData)


@dataclass(frozen=True, slots=True)
class StorageFieldMapping:
    field: SemanticId
    column: str
    column_type: str | None = None
    indexed: bool = False
    unique: bool = False
    nullable: bool | None = None

    def __post_init__(self) -> None:
        if not self.column:
            raise ValueError("storage field mappings require a column name")


@dataclass(frozen=True, slots=True)
class StorageMapping:
    id: SemanticId
    name: Name
    schema: SemanticId
    source: str
    fields: tuple[StorageFieldMapping, ...] = ()
    primary_key: tuple[SemanticId, ...] = ()
    indexes: tuple[tuple[SemanticId, ...], ...] = ()
    data: KernelData = field(default_factory=KernelData)

    def __post_init__(self) -> None:
        if not self.source:
            raise ValueError("storage mappings require a source/table/collection name")
        _validate_unique_ids("storage fields", (item.field for item in self.fields))
        _validate_unique_ids("storage primary key", self.primary_key)


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
        _validate_unique_ids("nested views", (item.id for item in self.parts))


class WorkflowStepKind(str, Enum):
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
        _validate_frozen_object("compensation input bindings", self.input_bindings)


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
class WorkflowFacets:
    trigger: TriggerFacet | None = None
    access: AccessFacet | None = None
    execution: ExecutionFacet | None = None
    events: EventsFacet | None = None
    durable: bool = False
    timeout_seconds: int | None = None


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


@dataclass(frozen=True, slots=True)
class GroupFacets:
    access: AccessFacet | None = None
    execution: ExecutionFacet | None = None


@dataclass(frozen=True, slots=True)
class Group:
    id: SemanticId
    name: Name
    path: tuple[str, ...] = ()
    schemas: tuple[Schema, ...] = ()
    operations: tuple[Operation, ...] = ()
    views: tuple[View, ...] = ()
    storage_mappings: tuple[StorageMapping, ...] = ()
    workflows: tuple[Workflow, ...] = ()
    policies: tuple[Policy, ...] = ()
    events: tuple[Event, ...] = ()
    groups: tuple[Group, ...] = ()
    facets: GroupFacets = field(default_factory=GroupFacets)
    data: KernelData = field(default_factory=KernelData)

    def __post_init__(self) -> None:
        if any(not part or "/" in part or "\\" in part for part in self.path):
            raise ValueError("group path parts must be non-empty path segments")
        _validate_unique_ids("nested groups", (item.id for item in self.groups))

    @property
    def storage(self) -> StorageNamespace:
        return StorageNamespace(self.storage_mappings)


@dataclass(frozen=True, slots=True)
class StorageNamespace:
    mappings: tuple[StorageMapping, ...]


@dataclass(frozen=True, slots=True)
class Contract:
    id: SemanticId
    name: Name
    groups: tuple[Group, ...]
    version: str | None = None
    data: KernelData = field(default_factory=KernelData)

    def __post_init__(self) -> None:
        if not self.groups:
            raise ValueError("contracts require at least one group")
        _validate_unique_ids("contract groups", (item.id for item in self.groups))


def walk_groups(groups: tuple[Group, ...]) -> tuple[Group, ...]:
    result: list[Group] = []

    def visit(group: Group) -> None:
        result.append(group)
        for child in group.groups:
            visit(child)

    for group in groups:
        visit(group)
    return tuple(result)


def type_references(expression: TypeExpression) -> tuple[SemanticId, ...]:
    result: list[SemanticId] = []
    if expression.reference is not None:
        result.append(expression.reference)
    for argument in expression.arguments:
        result.extend(type_references(argument))
    return tuple(result)


def _semantic_id(value: SemanticId | str) -> SemanticId:
    return value if isinstance(value, SemanticId) else SemanticId(value)


def _validate_unique_ids(label: str, values: object) -> None:
    materialized = tuple(values)  # type: ignore[arg-type]
    if len(materialized) != len(set(materialized)):
        raise ValueError(f"{label} must be unique")


def _validate_pairs(label: str, values: tuple[tuple[str, object], ...]) -> None:
    keys = tuple(key for key, _ in values)
    if len(keys) != len(set(keys)):
        raise ValueError(f"{label} keys must be unique")
    if tuple(sorted(values, key=lambda item: item[0])) != values:
        raise ValueError(f"{label} must be sorted by key")


def _validate_frozen_object(label: str, value: FrozenObject) -> None:
    _validate_pairs(label, value)
