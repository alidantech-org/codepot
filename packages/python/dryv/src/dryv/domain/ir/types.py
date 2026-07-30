from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .base import JsonScalar, SemanticId, semantic_id


class TypeKind(StrEnum):
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
        if self.kind is TypeKind.TUPLE and not self.arguments:
            raise ValueError("tuple type expressions require at least one member")

    @classmethod
    def primitive(cls, name: str) -> TypeExpression:
        return cls(TypeKind.PRIMITIVE, name=name)

    @classmethod
    def reference_to(cls, value: SemanticId | str) -> TypeExpression:
        return cls(TypeKind.REFERENCE, reference=semantic_id(value))

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


def type_references(expression: TypeExpression) -> tuple[SemanticId, ...]:
    references: list[SemanticId] = []
    if expression.reference is not None:
        references.append(expression.reference)
    for argument in expression.arguments:
        references.extend(type_references(argument))
    return tuple(references)
