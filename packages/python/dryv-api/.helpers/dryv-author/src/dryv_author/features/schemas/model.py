from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from dryv.ir import FieldCapabilities

from dryv_author.core import PropertyRef, SchemaRef
from dryv_author.features.properties import FieldOptions


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
class FieldSpec:
    annotation: object | None = None
    property: PropertyRef[object] | None = None
    schema: SchemaRef[object] | None = None
    options: FieldOptions = field(default_factory=FieldOptions)
    capabilities: FieldCapabilities = field(default_factory=FieldCapabilities)

    def __post_init__(self) -> None:
        if sum(value is not None for value in (self.annotation, self.property, self.schema)) != 1:
            raise ValueError("field spec requires exactly one type source")


@dataclass(frozen=True, slots=True)
class FieldDeclaration:
    name: str
    annotation: object | None = None
    property: PropertyRef[object] | None = None
    schema: SchemaRef[object] | None = None
    options: FieldOptions = field(default_factory=FieldOptions)
    capabilities: FieldCapabilities = field(default_factory=FieldCapabilities)

    def __post_init__(self) -> None:
        if not self.name or self.name.strip() != self.name:
            raise ValueError("field name must be a non-empty trimmed string")
        if sum(value is not None for value in (self.annotation, self.property, self.schema)) != 1:
            raise ValueError("field requires exactly one type source")


@dataclass(frozen=True, slots=True)
class ProjectionStep:
    operation: str
    fields: tuple[str, ...] = ()
    additions: tuple[FieldDeclaration, ...] = ()

    def __post_init__(self) -> None:
        if self.operation not in {"pick", "omit", "partial", "extend"}:
            raise ValueError(f"unsupported projection operation: {self.operation}")
        if len(self.fields) != len(set(self.fields)):
            raise ValueError("projection fields must be unique")
        if self.operation == "extend" and not self.additions:
            raise ValueError("extend projections require additions")
        if self.operation != "extend" and self.additions:
            raise ValueError("only extend projections accept additions")


@dataclass(frozen=True, slots=True)
class SchemaDeclaration:
    kind: SchemaDeclarationKind = SchemaDeclarationKind.OBJECT
    fields: tuple[FieldDeclaration, ...] = ()
    enum_values: tuple[str, ...] = ()
    alias_of: object | None = None
    item_type: object | None = None
    literal: str | int | float | bool | None = None
    extends: SchemaRef[object] | None = None
    source: SchemaRef[object] | None = None
    projections: tuple[ProjectionStep, ...] = ()

    def __post_init__(self) -> None:
        names = tuple(item.name for item in self.fields)
        if len(names) != len(set(names)):
            raise ValueError("schema field names must be unique")
        if self.kind is SchemaDeclarationKind.ENUM:
            if not self.enum_values or len(self.enum_values) != len(set(self.enum_values)):
                raise ValueError("enum schemas require unique values")
        if self.kind is SchemaDeclarationKind.ALIAS and self.alias_of is None:
            raise ValueError("alias schemas require alias_of")
        if self.kind is SchemaDeclarationKind.ARRAY and self.item_type is None:
            raise ValueError("array schemas require item_type")
        if self.source is not None and not self.projections:
            raise ValueError("projected schemas require projection steps")
        if self.source is None and self.projections:
            raise ValueError("projection steps require a source schema")


def field_of(value: object, *, required: bool = True, nullable: bool = False, readonly: bool = False, minimum: int | float | None = None, maximum: int | float | None = None, min_length: int | None = None, max_length: int | None = None, pattern: str | None = None, format: str | None = None, capabilities: FieldCapabilities | None = None) -> FieldSpec:
    options = FieldOptions(required=required, nullable=nullable, readonly=readonly, minimum=minimum, maximum=maximum, min_length=min_length, max_length=max_length, pattern=pattern, format=format)
    parsed_capabilities = capabilities or FieldCapabilities()
    if isinstance(value, PropertyRef):
        return FieldSpec(property=value, options=options, capabilities=parsed_capabilities)
    if isinstance(value, SchemaRef):
        return FieldSpec(schema=value, options=options, capabilities=parsed_capabilities)
    return FieldSpec(annotation=value, options=options, capabilities=parsed_capabilities)


def fields_from_mapping(values: dict[str, object]) -> tuple[FieldDeclaration, ...]:
    result: list[FieldDeclaration] = []
    for name, value in values.items():
        if isinstance(value, FieldSpec):
            result.append(FieldDeclaration(name, value.annotation, value.property, value.schema, value.options, value.capabilities))
        elif isinstance(value, PropertyRef):
            result.append(FieldDeclaration(name, property=value))
        elif isinstance(value, SchemaRef):
            result.append(FieldDeclaration(name, schema=value))
        else:
            result.append(FieldDeclaration(name, annotation=value))
    return tuple(result)


__all__ = ["FieldDeclaration", "FieldSpec", "ProjectionStep", "SchemaDeclaration", "SchemaDeclarationKind", "field_of", "fields_from_mapping"]
