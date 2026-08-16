from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Generic, TypeVar

T = TypeVar("T")
TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class RefKind(StrEnum):
    GROUP = "group"
    PROPERTY = "property"
    SCHEMA = "schema"
    FIELD = "field"
    FAILURE = "failure"
    EVENT = "event"
    OPERATION = "operation"
    STORAGE = "storage"
    VALUE_SOURCE = "value_source"
    POLICY = "policy"
    WORKFLOW = "workflow"
    VIEW = "view"
    PRESENTATION = "presentation"


@dataclass(frozen=True, slots=True)
class RefUsage(Generic[T]):
    ref: AuthorRef[T]
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
class AuthorRef(Generic[T]):
    author_key: str
    declaration_id: str
    kind: RefKind

    def __post_init__(self) -> None:
        if not self.author_key or not self.declaration_id:
            raise ValueError("author references require author_key and declaration_id")

    def optional(self) -> RefUsage[T]:
        return RefUsage(self, required=False)

    def required(self) -> RefUsage[T]:
        return RefUsage(self, required=True)

    def nullable(self) -> RefUsage[T]:
        return RefUsage(self, nullable=True)

    def array(self) -> RefUsage[T]:
        return RefUsage(self, array=True)


@dataclass(frozen=True, slots=True)
class GroupRef(AuthorRef[object]):
    pass


@dataclass(frozen=True, slots=True)
class PropertyRef(AuthorRef[T], Generic[T]):
    pass


@dataclass(frozen=True, slots=True)
class SchemaRef(AuthorRef[T], Generic[T]):
    def field(self, name: str) -> FieldRef[object]:
        from .naming import slug

        return FieldRef(
            self.author_key,
            f"{self.declaration_id}/field/{slug(name)}",
            RefKind.FIELD,
            self.declaration_id,
            name,
        )


@dataclass(frozen=True, slots=True)
class FieldRef(AuthorRef[T], Generic[T]):
    schema_declaration_id: str = ""
    field_name: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.kind is not RefKind.FIELD:
            raise ValueError("FieldRef must use field kind")
        if not self.schema_declaration_id or not self.field_name:
            raise ValueError("field references require schema declaration and field name")


@dataclass(frozen=True, slots=True)
class FailureRef(AuthorRef[object]):
    pass


@dataclass(frozen=True, slots=True)
class EventRef(AuthorRef[T], Generic[T]):
    pass


@dataclass(frozen=True, slots=True)
class OperationRef(AuthorRef[tuple[TInput, TOutput]], Generic[TInput, TOutput]):
    pass


@dataclass(frozen=True, slots=True)
class StorageRef(AuthorRef[T], Generic[T]):
    pass


@dataclass(frozen=True, slots=True)
class ValueSourceRef(AuthorRef[T], Generic[T]):
    pass


@dataclass(frozen=True, slots=True)
class PolicyRef(AuthorRef[object]):
    pass


@dataclass(frozen=True, slots=True)
class WorkflowRef(AuthorRef[object]):
    pass


@dataclass(frozen=True, slots=True)
class ViewRef(AuthorRef[object]):
    pass


@dataclass(frozen=True, slots=True)
class PresentationRef(AuthorRef[object]):
    pass


_REF_TYPES: dict[RefKind, type[AuthorRef[object]]] = {
    RefKind.GROUP: GroupRef,
    RefKind.PROPERTY: PropertyRef,
    RefKind.SCHEMA: SchemaRef,
    RefKind.FAILURE: FailureRef,
    RefKind.EVENT: EventRef,
    RefKind.OPERATION: OperationRef,
    RefKind.STORAGE: StorageRef,
    RefKind.VALUE_SOURCE: ValueSourceRef,
    RefKind.POLICY: PolicyRef,
    RefKind.WORKFLOW: WorkflowRef,
    RefKind.VIEW: ViewRef,
    RefKind.PRESENTATION: PresentationRef,
}


def make_ref(author_key: str, declaration_id: str, kind: RefKind) -> AuthorRef[object]:
    if kind is RefKind.FIELD:
        raise ValueError("field references must be created from SchemaRef.field()")
    return _REF_TYPES[kind](author_key, declaration_id, kind)


__all__ = [
    "AuthorRef", "EventRef", "FailureRef", "FieldRef", "GroupRef", "OperationRef",
    "PolicyRef", "PresentationRef", "PropertyRef", "RefKind", "RefUsage", "SchemaRef",
    "StorageRef", "ValueSourceRef", "ViewRef", "WorkflowRef", "make_ref",
]
