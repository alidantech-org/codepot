from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field as dc_field
from enum import StrEnum
from types import NoneType
from typing import get_args, get_origin

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
        if type(self.required) is not bool:
            raise TypeError("required must be bool")
        if type(self.nullable) is not bool:
            raise TypeError("nullable must be bool")
        if type(self.readonly) is not bool:
            raise TypeError("readonly must be bool")
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
        if self.pattern is not None and not isinstance(self.pattern, str):
            raise TypeError("pattern must be str or None")
        if self.format is not None and not isinstance(self.format, str):
            raise TypeError("format must be str or None")
        if self.description is not None and not isinstance(self.description, str):
            raise TypeError("description must be str or None")


@dataclass(frozen=True, slots=True)
class PropertyDeclaration:
    annotation: object
    options: FieldOptions = dc_field(default_factory=FieldOptions)


@dataclass(frozen=True, slots=True)
class FieldSpec:
    annotation: object | None = None
    property_ref: PropertyRef[object] | None = None
    schema_ref: SchemaRef[object] | None = None
    options: FieldOptions = dc_field(default_factory=FieldOptions)

    def __post_init__(self) -> None:
        sources = sum(value is not None for value in (self.annotation, self.property_ref, self.schema_ref))
        if sources != 1:
            raise ValueError("field spec requires exactly one type source")


@dataclass(frozen=True, slots=True)
class FieldDeclaration:
    name: str
    annotation: object | None = None
    property_ref: PropertyRef[object] | None = None
    schema_ref: SchemaRef[object] | None = None
    options: FieldOptions = dc_field(default_factory=FieldOptions)

    def __post_init__(self) -> None:
        if not self.name or self.name.strip() != self.name:
            raise ValueError("field name must be a non-empty trimmed string")
        sources = sum(value is not None for value in (self.annotation, self.property_ref, self.schema_ref))
        if sources != 1:
            raise ValueError("field requires exactly one type source")


@dataclass(frozen=True, slots=True)
class ProjectionStep:
    operation: str
    fields: tuple[str, ...] = ()
    additions: tuple[FieldDeclaration, ...] = ()

    def __post_init__(self) -> None:
        supported = {
            "pick",
            "omit",
            "partial",
            "extend",
            "derive_create",
            "derive_update",
            "derive_read",
            "derive_query",
        }
        if self.operation not in supported:
            raise ValueError(f"unsupported projection operation: {self.operation}")
        if len(self.fields) != len(set(self.fields)):
            raise ValueError("projection fields must be unique")
        addition_names = tuple(item.name for item in self.additions)
        if len(addition_names) != len(set(addition_names)):
            raise ValueError("projection additions must have unique names")
        if self.operation == "extend" and not self.additions:
            raise ValueError("extend projections require additions")
        if self.operation != "extend" and self.additions:
            raise ValueError("only extend projections accept additions")


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
            if any(not isinstance(value, str) or not value for value in self.enum_values):
                raise TypeError("core enum values must be non-empty strings")
        if self.kind is SchemaDeclarationKind.ALIAS and self.alias_of is None:
            raise ValueError("alias schemas require alias_of")
        if self.source_schema is not None and not self.projection_steps:
            raise ValueError("projected schemas require projection steps")


def schema_field(
    annotation: object | PropertyRef[object] | SchemaRef[object],
    *,
    options: FieldOptions | None = None,
    required: bool | None = None,
    nullable: bool | None = None,
    readonly: bool | None = None,
    minimum: int | float | None = None,
    maximum: int | float | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
    pattern: str | None = None,
    format: str | None = None,
    description: str | None = None,
) -> FieldSpec:
    explicit = any(
        value is not None
        for value in (
            required,
            nullable,
            readonly,
            minimum,
            maximum,
            min_length,
            max_length,
            pattern,
            format,
            description,
        )
    )
    if options is not None and explicit:
        raise ValueError("pass either options or explicit field option arguments, not both")
    parsed = options or FieldOptions(
        required=True if required is None else required,
        nullable=False if nullable is None else nullable,
        readonly=False if readonly is None else readonly,
        minimum=minimum,
        maximum=maximum,
        min_length=min_length,
        max_length=max_length,
        pattern=pattern,
        format=format,
        description=description,
    )
    if isinstance(annotation, PropertyRef):
        return FieldSpec(property_ref=annotation, options=parsed)
    if isinstance(annotation, SchemaRef):
        return FieldSpec(schema_ref=annotation, options=parsed)
    return FieldSpec(annotation=annotation, options=parsed)


field = schema_field


def fields_from_mapping(values: Mapping[str, object]) -> tuple[FieldDeclaration, ...]:
    result: list[FieldDeclaration] = []
    for name, value in values.items():
        if isinstance(value, FieldSpec):
            result.append(
                FieldDeclaration(
                    name,
                    value.annotation,
                    value.property_ref,
                    value.schema_ref,
                    value.options,
                )
            )
        elif isinstance(value, PropertyRef):
            result.append(FieldDeclaration(name, property_ref=value))
        elif isinstance(value, SchemaRef):
            result.append(FieldDeclaration(name, schema_ref=value))
        else:
            nullable = NoneType in get_args(value) if get_origin(value) is not None else False
            result.append(
                FieldDeclaration(name, annotation=value, options=FieldOptions(nullable=nullable))
            )
    return tuple(result)


def expand_projection(
    source_fields: tuple[FieldDeclaration, ...],
    steps: tuple[ProjectionStep, ...],
) -> tuple[FieldDeclaration, ...]:
    fields = list(source_fields)
    for step in steps:
        names = {item.name for item in fields}
        missing = tuple(name for name in step.fields if name not in names)
        if missing:
            raise ValueError(f"projection references unknown fields: {', '.join(missing)}")
        if step.operation == "pick":
            selected = set(step.fields)
            fields = [item for item in fields if item.name in selected]
        elif step.operation == "omit":
            omitted = set(step.fields)
            fields = [item for item in fields if item.name not in omitted]
        elif step.operation in {"partial", "derive_update", "derive_query"}:
            selected = set(step.fields)
            fields = [
                FieldDeclaration(
                    item.name,
                    item.annotation,
                    item.property_ref,
                    item.schema_ref,
                    FieldOptions(
                        required=False if not selected or item.name in selected else item.options.required,
                        nullable=item.options.nullable,
                        readonly=item.options.readonly,
                        minimum=item.options.minimum,
                        maximum=item.options.maximum,
                        min_length=item.options.min_length,
                        max_length=item.options.max_length,
                        pattern=item.options.pattern,
                        format=item.options.format,
                        description=item.options.description,
                    ),
                )
                for item in fields
            ]
        elif step.operation == "derive_create":
            fields = [item for item in fields if not item.options.readonly]
        elif step.operation == "derive_read":
            fields = list(fields)
        elif step.operation == "extend":
            collisions = names.intersection(item.name for item in step.additions)
            if collisions:
                raise ValueError(f"projection additions collide: {', '.join(sorted(collisions))}")
            fields.extend(step.additions)
    return tuple(fields)
