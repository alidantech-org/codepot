from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from .base import JsonScalar, KernelData, SemanticId
from .naming import Name
from .types import TypeExpression


class SchemaKind(StrEnum):
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
        keys = tuple(key for key, _ in self.origins)
        if tuple(sorted(keys)) != keys or len(keys) != len(set(keys)):
            raise ValueError("constraint origins must be sorted by unique key")


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
        field_ids = tuple(item.id for item in self.fields)
        if len(field_ids) != len(set(field_ids)):
            raise ValueError("schema field ids must be unique")
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
