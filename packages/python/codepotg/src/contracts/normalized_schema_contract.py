from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any

from contracts.api import ApiContract, ApiSchema
from contracts.normalized import (
    ContractCollection,
    ContractDiagnostic,
    DiagnosticCategory,
    DiagnosticLevel,
    PresenceValue,
    SchemaUse,
    SourceObject,
    contract_collection,
    presence_from_mapping,
    source_object,
)
from contracts.normalized_builders import build_schema_use
from contracts.source import FrozenMap, freeze_source_map


class SchemaBoundaryKind(StrEnum):
    """State of additional/unevaluated schema boundaries."""

    MISSING = "missing"
    ALLOWED = "allowed"
    FORBIDDEN = "forbidden"
    SCHEMA = "schema"
    MALFORMED = "malformed"


@dataclass(frozen=True)
class NormalizedSchemaBoundary:
    """Boolean or schema-valued boundary such as additionalProperties."""

    kind: SchemaBoundaryKind = SchemaBoundaryKind.MISSING
    value: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    schema: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    diagnostics: tuple[ContractDiagnostic, ...] = ()

    @property
    def is_allowed(self) -> bool:
        return self.kind == SchemaBoundaryKind.ALLOWED

    @property
    def is_forbidden(self) -> bool:
        return self.kind == SchemaBoundaryKind.FORBIDDEN

    @property
    def is_typed(self) -> bool:
        return self.kind == SchemaBoundaryKind.SCHEMA


@dataclass(frozen=True)
class NormalizedSchemaKeywordView:
    """Complete additive JSON Schema/OpenAPI schema keyword contract."""

    id: str
    source: SourceObject = field(default_factory=SourceObject)
    title: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    summary: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    description: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    types: tuple[str, ...] = ()
    format: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    nullable: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    default: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    const: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    example: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    examples: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    enum: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    required: tuple[str, ...] = ()

    minimum: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    maximum: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    exclusive_minimum: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    exclusive_maximum: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    multiple_of: PresenceValue[Any] = field(default_factory=PresenceValue.missing)

    min_length: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    max_length: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    pattern: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    content_encoding: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    content_media_type: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    content_schema: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)

    items: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    prefix_items: tuple[SchemaUse[ApiSchema], ...] = ()
    contains: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    min_contains: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    max_contains: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    min_items: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    max_items: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    unique_items: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    unevaluated_items: NormalizedSchemaBoundary = field(
        default_factory=NormalizedSchemaBoundary
    )

    properties: Mapping[str, SchemaUse[ApiSchema]] = field(
        default_factory=lambda: MappingProxyType({})
    )
    additional_properties: NormalizedSchemaBoundary = field(
        default_factory=NormalizedSchemaBoundary
    )
    pattern_properties: Mapping[str, SchemaUse[ApiSchema]] = field(
        default_factory=lambda: MappingProxyType({})
    )
    property_names: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    min_properties: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    max_properties: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    dependent_required: Mapping[str, tuple[str, ...]] = field(
        default_factory=lambda: MappingProxyType({})
    )
    dependent_schemas: Mapping[str, SchemaUse[ApiSchema]] = field(
        default_factory=lambda: MappingProxyType({})
    )
    unevaluated_properties: NormalizedSchemaBoundary = field(
        default_factory=NormalizedSchemaBoundary
    )

    all_of: tuple[SchemaUse[ApiSchema], ...] = ()
    any_of: tuple[SchemaUse[ApiSchema], ...] = ()
    one_of: tuple[SchemaUse[ApiSchema], ...] = ()
    not_schema: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    if_schema: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    then_schema: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    else_schema: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)

    defs: Mapping[str, SchemaUse[ApiSchema]] = field(
        default_factory=lambda: MappingProxyType({})
    )
    discriminator: FrozenMap = field(default_factory=FrozenMap)
    read_only: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    write_only: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    deprecated: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    external_docs: FrozenMap = field(default_factory=FrozenMap)
    schema_id: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    anchor: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    dynamic_anchor: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    dynamic_ref: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    dialect: PresenceValue[Any] = field(default_factory=PresenceValue.missing)

    @property
    def name(self) -> str:
        return self.id

    @property
    def compositions(self) -> Mapping[str, tuple[SchemaUse[ApiSchema], ...]]:
        return MappingProxyType(
            {
                "allOf": self.all_of,
                "anyOf": self.any_of,
                "oneOf": self.one_of,
            }
        )

    @property
    def diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        values = list(self.source.diagnostics)
        values.extend(self.additional_properties.diagnostics)
        values.extend(self.unevaluated_items.diagnostics)
        values.extend(self.unevaluated_properties.diagnostics)
        for use in self._schema_uses():
            values.extend(use.diagnostics)
        return tuple(values)

    def _schema_uses(self) -> tuple[SchemaUse[ApiSchema], ...]:
        return (
            self.content_schema,
            self.items,
            self.contains,
            self.property_names,
            self.not_schema,
            self.if_schema,
            self.then_schema,
            self.else_schema,
            self.additional_properties.schema,
            self.unevaluated_items.schema,
            self.unevaluated_properties.schema,
            *self.prefix_items,
            *self.properties.values(),
            *self.pattern_properties.values(),
            *self.dependent_schemas.values(),
            *self.defs.values(),
            *self.all_of,
            *self.any_of,
            *self.one_of,
        )


@dataclass(frozen=True)
class NormalizedSchemaContract:
    """Deterministic complete schema-keyword registry."""

    schemas: ContractCollection[NormalizedSchemaKeywordView] = field(
        default_factory=ContractCollection
    )
    dialect: PresenceValue[Any] = field(default_factory=PresenceValue.missing)

    @property
    def all(self) -> tuple[NormalizedSchemaKeywordView, ...]:
        return self.schemas.all

    @property
    def by_id(self) -> Mapping[str, NormalizedSchemaKeywordView]:
        return self.schemas.by_id

    @property
    def count(self) -> int:
        return self.schemas.count

    @property
    def diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        return tuple(
            diagnostic
            for schema in self.schemas.all
            for diagnostic in schema.diagnostics
        )

    @property
    def unresolved_count(self) -> int:
        return sum(
            diagnostic.category == DiagnosticCategory.UNRESOLVED
            for diagnostic in self.diagnostics
        )

    @property
    def loss_count(self) -> int:
        return sum(
            diagnostic.category == DiagnosticCategory.LOST
            for diagnostic in self.diagnostics
        )


def build_normalized_schema_contract(
    api: ApiContract,
    raw: Mapping[str, Any] | None,
) -> NormalizedSchemaContract:
    """Build complete schema facts without changing compatibility schema objects."""

    document = _mapping(raw)
    schemas_raw = _mapping(_mapping(document.get("components")).get("schemas"))
    schema_targets = {schema.ref: schema for schema in api.schemas.all}
    values = tuple(
        _schema(
            schema.id,
            _mapping(schemas_raw.get(schema.id)),
            owner=schema.ref,
            schema_targets=schema_targets,
        )
        for schema in api.schemas.all
    )
    return NormalizedSchemaContract(
        schemas=contract_collection(values),
        dialect=presence_from_mapping(document, "jsonSchemaDialect", source_path="$"),
    )


def _schema(
    name: str,
    raw: Mapping[str, Any],
    *,
    owner: str,
    schema_targets: Mapping[str, ApiSchema],
) -> NormalizedSchemaKeywordView:
    source_path = f"components.schemas.{name}"
    use = lambda value, suffix: build_schema_use(
        value,
        owner=owner,
        source_path=f"{source_path}.{suffix}",
        schema_targets=schema_targets,
    )
    sequence_uses = lambda key: tuple(
        use(value, f"{key}.{index}")
        for index, value in enumerate(_sequence(raw.get(key)))
    )
    mapping_uses = lambda key: MappingProxyType(
        {
            str(item_name): use(value, f"{key}.{item_name}")
            for item_name, value in _mapping(raw.get(key)).items()
        }
    )
    return NormalizedSchemaKeywordView(
        id=name,
        source=source_object(raw, source_path=source_path, known_keys=_SCHEMA_KEYS),
        title=presence_from_mapping(raw, "title", source_path=source_path),
        summary=presence_from_mapping(raw, "summary", source_path=source_path),
        description=presence_from_mapping(raw, "description", source_path=source_path),
        types=_types(raw.get("type")),
        format=presence_from_mapping(raw, "format", source_path=source_path),
        nullable=presence_from_mapping(raw, "nullable", source_path=source_path),
        default=presence_from_mapping(raw, "default", source_path=source_path),
        const=presence_from_mapping(raw, "const", source_path=source_path),
        example=presence_from_mapping(raw, "example", source_path=source_path),
        examples=presence_from_mapping(raw, "examples", source_path=source_path),
        enum=presence_from_mapping(raw, "enum", source_path=source_path),
        required=tuple(str(item) for item in _sequence(raw.get("required"))),
        minimum=presence_from_mapping(raw, "minimum", source_path=source_path),
        maximum=presence_from_mapping(raw, "maximum", source_path=source_path),
        exclusive_minimum=presence_from_mapping(
            raw, "exclusiveMinimum", source_path=source_path
        ),
        exclusive_maximum=presence_from_mapping(
            raw, "exclusiveMaximum", source_path=source_path
        ),
        multiple_of=presence_from_mapping(raw, "multipleOf", source_path=source_path),
        min_length=presence_from_mapping(raw, "minLength", source_path=source_path),
        max_length=presence_from_mapping(raw, "maxLength", source_path=source_path),
        pattern=presence_from_mapping(raw, "pattern", source_path=source_path),
        content_encoding=presence_from_mapping(
            raw, "contentEncoding", source_path=source_path
        ),
        content_media_type=presence_from_mapping(
            raw, "contentMediaType", source_path=source_path
        ),
        content_schema=use(raw.get("contentSchema"), "contentSchema"),
        items=use(raw.get("items"), "items"),
        prefix_items=sequence_uses("prefixItems"),
        contains=use(raw.get("contains"), "contains"),
        min_contains=presence_from_mapping(raw, "minContains", source_path=source_path),
        max_contains=presence_from_mapping(raw, "maxContains", source_path=source_path),
        min_items=presence_from_mapping(raw, "minItems", source_path=source_path),
        max_items=presence_from_mapping(raw, "maxItems", source_path=source_path),
        unique_items=presence_from_mapping(raw, "uniqueItems", source_path=source_path),
        unevaluated_items=_boundary(
            raw,
            "unevaluatedItems",
            owner=owner,
            source_path=source_path,
            schema_targets=schema_targets,
        ),
        properties=mapping_uses("properties"),
        additional_properties=_boundary(
            raw,
            "additionalProperties",
            owner=owner,
            source_path=source_path,
            schema_targets=schema_targets,
        ),
        pattern_properties=mapping_uses("patternProperties"),
        property_names=use(raw.get("propertyNames"), "propertyNames"),
        min_properties=presence_from_mapping(raw, "minProperties", source_path=source_path),
        max_properties=presence_from_mapping(raw, "maxProperties", source_path=source_path),
        dependent_required=MappingProxyType(
            {
                str(item_name): tuple(str(item) for item in _sequence(value))
                for item_name, value in _mapping(raw.get("dependentRequired")).items()
            }
        ),
        dependent_schemas=mapping_uses("dependentSchemas"),
        unevaluated_properties=_boundary(
            raw,
            "unevaluatedProperties",
            owner=owner,
            source_path=source_path,
            schema_targets=schema_targets,
        ),
        all_of=sequence_uses("allOf"),
        any_of=sequence_uses("anyOf"),
        one_of=sequence_uses("oneOf"),
        not_schema=use(raw.get("not"), "not"),
        if_schema=use(raw.get("if"), "if"),
        then_schema=use(raw.get("then"), "then"),
        else_schema=use(raw.get("else"), "else"),
        defs=mapping_uses("$defs"),
        discriminator=freeze_source_map(_mapping(raw.get("discriminator"))),
        read_only=presence_from_mapping(raw, "readOnly", source_path=source_path),
        write_only=presence_from_mapping(raw, "writeOnly", source_path=source_path),
        deprecated=presence_from_mapping(raw, "deprecated", source_path=source_path),
        external_docs=freeze_source_map(_mapping(raw.get("externalDocs"))),
        schema_id=presence_from_mapping(raw, "$id", source_path=source_path),
        anchor=presence_from_mapping(raw, "$anchor", source_path=source_path),
        dynamic_anchor=presence_from_mapping(raw, "$dynamicAnchor", source_path=source_path),
        dynamic_ref=presence_from_mapping(raw, "$dynamicRef", source_path=source_path),
        dialect=presence_from_mapping(raw, "$schema", source_path=source_path),
    )


def _boundary(
    raw: Mapping[str, Any],
    key: str,
    *,
    owner: str,
    source_path: str,
    schema_targets: Mapping[str, ApiSchema],
) -> NormalizedSchemaBoundary:
    path = f"{source_path}.{key}"
    if key not in raw:
        return NormalizedSchemaBoundary(
            value=PresenceValue.missing(source_path=path),
            schema=SchemaUse(source_path=path),
        )
    value = raw[key]
    presence = PresenceValue.authored(value, source_path=path)
    if value is True:
        return NormalizedSchemaBoundary(kind=SchemaBoundaryKind.ALLOWED, value=presence)
    if value is False:
        return NormalizedSchemaBoundary(kind=SchemaBoundaryKind.FORBIDDEN, value=presence)
    if isinstance(value, Mapping):
        return NormalizedSchemaBoundary(
            kind=SchemaBoundaryKind.SCHEMA,
            value=presence,
            schema=build_schema_use(
                value,
                owner=owner,
                source_path=path,
                schema_targets=schema_targets,
            ),
        )
    diagnostic = ContractDiagnostic(
        category=DiagnosticCategory.MALFORMED,
        level=DiagnosticLevel.WARNING,
        message=f"{key} must be a boolean or schema object.",
        source_path=path,
        value=value,
        owner=owner,
    )
    return NormalizedSchemaBoundary(
        kind=SchemaBoundaryKind.MALFORMED,
        value=presence,
        diagnostics=(diagnostic,),
    )


def _types(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list | tuple):
        return tuple(str(item) for item in value)
    return ()


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> tuple[Any, ...]:
    return tuple(value) if isinstance(value, list | tuple) else ()


_SCHEMA_KEYS = {
    "$anchor",
    "$comment",
    "$defs",
    "$dynamicAnchor",
    "$dynamicRef",
    "$id",
    "$ref",
    "$schema",
    "additionalProperties",
    "allOf",
    "anyOf",
    "const",
    "contains",
    "contentEncoding",
    "contentMediaType",
    "contentSchema",
    "default",
    "dependentRequired",
    "dependentSchemas",
    "deprecated",
    "description",
    "discriminator",
    "else",
    "enum",
    "example",
    "examples",
    "exclusiveMaximum",
    "exclusiveMinimum",
    "externalDocs",
    "format",
    "if",
    "items",
    "maxContains",
    "maxItems",
    "maxLength",
    "maxProperties",
    "maximum",
    "minContains",
    "minItems",
    "minLength",
    "minProperties",
    "minimum",
    "multipleOf",
    "not",
    "nullable",
    "oneOf",
    "pattern",
    "patternProperties",
    "prefixItems",
    "properties",
    "propertyNames",
    "readOnly",
    "required",
    "summary",
    "then",
    "title",
    "type",
    "unevaluatedItems",
    "unevaluatedProperties",
    "uniqueItems",
    "writeOnly",
    "xml",
    "x-codegen",
}
