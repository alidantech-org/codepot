from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from .kinds import RefKind

T = TypeVar("T")
TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


@dataclass(frozen=True, slots=True, order=True)
class RefIdentity:
    author_id: str
    declaration_id: str
    kind: RefKind

    def __post_init__(self) -> None:
        if not self.author_id or not self.declaration_id:
            raise ValueError("ref identity values must not be empty")


@dataclass(frozen=True, slots=True)
class RefUsage(Generic[T]):
    ref: Ref[T]
    required: bool | None = None
    nullable: bool = False
    array: bool = False

    def optional(self) -> RefUsage[T]:
        return RefUsage(self.ref, required=False, nullable=self.nullable, array=self.array)

    def required_value(self) -> RefUsage[T]:
        return RefUsage(self.ref, required=True, nullable=self.nullable, array=self.array)

    def nullable_value(self) -> RefUsage[T]:
        return RefUsage(self.ref, required=self.required, nullable=True, array=self.array)

    def array_value(self) -> RefUsage[T]:
        return RefUsage(self.ref, required=self.required, nullable=self.nullable, array=True)


@dataclass(frozen=True, slots=True)
class Ref(Generic[T]):
    identity: RefIdentity

    @property
    def kind(self) -> RefKind:
        return self.identity.kind

    @property
    def declaration_id(self) -> str:
        return self.identity.declaration_id

    def optional(self) -> RefUsage[T]:
        return RefUsage(self, required=False)

    def required(self) -> RefUsage[T]:
        return RefUsage(self, required=True)

    def nullable(self) -> RefUsage[T]:
        return RefUsage(self, nullable=True)

    def array(self) -> RefUsage[T]:
        return RefUsage(self, array=True)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.identity.kind.value}:{self.identity.declaration_id})"


@dataclass(frozen=True, slots=True)
class GroupRef(Ref[object]):
    pass


@dataclass(frozen=True, slots=True)
class PropertyRef(Ref[T], Generic[T]):
    pass


@dataclass(frozen=True, slots=True)
class SchemaRef(Ref[T], Generic[T]):
    pass


@dataclass(frozen=True, slots=True)
class FieldRef(Ref[T], Generic[T]):
    schema_declaration_id: str = ""
    field_name: str = ""


@dataclass(frozen=True, slots=True)
class OperationRef(Ref[tuple[TInput, TOutput]], Generic[TInput, TOutput]):
    pass


@dataclass(frozen=True, slots=True)
class EventRef(Ref[T], Generic[T]):
    pass


@dataclass(frozen=True, slots=True)
class PolicyRef(Ref[object]):
    pass


@dataclass(frozen=True, slots=True)
class StorageRef(Ref[T], Generic[T]):
    pass


@dataclass(frozen=True, slots=True)
class ViewRef(Ref[object]):
    pass


@dataclass(frozen=True, slots=True)
class WorkflowRef(Ref[object]):
    pass


@dataclass(frozen=True, slots=True)
class WorkflowStepRef(Ref[object]):
    pass


@dataclass(frozen=True, slots=True)
class ValueSourceRef(Ref[T], Generic[T]):
    pass


@dataclass(frozen=True, slots=True)
class PresentationRef(Ref[object]):
    pass
