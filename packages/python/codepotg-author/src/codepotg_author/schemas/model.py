from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from types import NoneType
from typing import Mapping, get_args, get_origin

from codepotg_author.refs import PropertyRef, SchemaRef


class SchemaDeclarationKind(StrEnum):
    OBJECT = "object"
    ENUM = "enum"
    ALIAS = "alias"
    ARRAY = "array"
    MAP = "map"
    TUPLE = "tuple"
    UNION = "union"
    INTERSECTION = "intersection"
    PRIMITIVE = "primitive"
    LITERAL = "literal"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class FieldOptions:
    required: bool = True
    nullable: bool = False
    readonly: bool = False
    minimum: int | float | None = None
    maximum: int | float | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    format: str | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        if type(self.required) is not bool or type(self.nullable) is not bool:
            raise TypeError("required and nullable must be bool")
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise ValueError("minimum must not exceed maximum")
        if self.min_length is not None and self.min_length < 0:
            raise ValueError("min_length must be non-negative")
        if self.max_length is not None and self.max_length < 0:
            raise ValueError("max_length must be non-negative")
        if self.min_length is not None and self.max_length is not None and self.min_length > self.max_length:
            raise ValueError("min_length must not exceed max_length")


@dataclass(frozen=True, slots=True)
class PropertyDeclaration:
    annotation: object
    options: FieldOptions = field(default_factory=FieldOptions)


@dataclass(frozen=True, slots=True)
class FieldDeclaration:
    name: str
    annotation: object | None = None
    property_ref: PropertyRef[object] | None = None
    schema_ref: SchemaRef[object] | None = None
    options: FieldOptions = field(default_factory=FieldOptions)

    def __post_init__(self) -> None:
        sources = sum(value is not None for value in (self.annotation, self.property_ref, self.schema_ref))
        if not self.name or sources != 1:
            raise ValueError("field requires a name and exactly one type source")


@dataclass(frozen=True, slots=True)
class ProjectionStep:
    operation: str
    fields: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.operation not in {"pick", "omit", "partial", "extend", "derive_create", "derive_update", "derive_read", "derive_query"}:
            raise ValueError(f"unsupported projection operation: {self.operation}")
        if len(self.fields) != len(set(self.fields)):
            raise ValueError("projection fields must be unique")


@dataclass(frozen=True, slots=True)
class SchemaDeclaration:
    kind: SchemaDeclarationKind
    fields: tuple[FieldDeclaration, ...] = ()
    enum_values: tuple[str, ...] = ()
    alias_of: object | None = None
    source_schema: SchemaRef[object] | None = None
    projection_steps: tuple[ProjectionStep, ...] = ()

    def __post_init__(self) -> None:
        names = tuple(item.name for item in self.fields)
        if len(names) != len(set(names)):
            raise ValueError("schema field names must be unique")
        if self.kind is SchemaDeclarationKind.ENUM:
            if not self.enum_values:
                raise ValueError("enum schemas require values")
            if len(self.enum_values) != len(set(self.enum_values)):
                raise ValueError("enum schema values must be unique")
        if self.kind is SchemaDeclarationKind.ALIAS and self.alias_of is None:
            raise ValueError("alias schemas require alias_of")


def field(
    annotation: object | PropertyRef[object] | SchemaRef[object],
    **options: object,
) -> tuple[object | None, PropertyRef[object] | None, SchemaRef[object] | None, FieldOptions]:
    parsed = FieldOptions(**options)  # type: ignore[arg-type]
    if isinstance(annotation, PropertyRef):
        return None, annotation, None, parsed
    if isinstance(annotation, SchemaRef):
        return None, None, annotation, parsed
    return annotation, None, None, parsed


def fields_from_mapping(values: Mapping[str, object]) -> tuple[FieldDeclaration, ...]:
    result: list[FieldDeclaration] = []
    for name, value in values.items():
        if isinstance(value, tuple) and len(value) == 4 and isinstance(value[3], FieldOptions):
            annotation, property_ref, schema_ref, options = value
            result.append(FieldDeclaration(name, annotation, property_ref, schema_ref, options))
        elif isinstance(value, PropertyRef):
            result.append(FieldDeclaration(name, property_ref=value))
        elif isinstance(value, SchemaRef):
            result.append(FieldDeclaration(name, schema_ref=value))
        else:
            nullable = NoneType in get_args(value) if get_origin(value) is not None else False
            result.append(FieldDeclaration(name, annotation=value, options=FieldOptions(nullable=nullable)))
    return tuple(result)
