from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from contracts.api import ApiContract, ApiField, ApiOperation, ApiResource, ApiSchema
from contracts.normalized import (
    ContractCollection,
    ContractDiagnostic,
    ContractReference,
    DiagnosticCategory,
    DiagnosticLevel,
    PresenceValue,
    SchemaUse,
    SourceObject,
    StructuredNotes,
    contract_collection,
    presence_from_mapping,
    source_object,
    structured_notes,
)
from contracts.normalized_builders import build_schema_use
from contracts.source import FrozenMap


@dataclass(frozen=True)
class NormalizedSchemaConstraints:
    default: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    const: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    example: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    examples: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
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
    min_items: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    max_items: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    unique_items: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    min_contains: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    max_contains: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    min_properties: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    max_properties: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    read_only: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    write_only: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    deprecated: PresenceValue[Any] = field(default_factory=PresenceValue.missing)


@dataclass(frozen=True)
class NormalizedComposition:
    kind: str
    branches: tuple[SchemaUse[ApiSchema], ...] = ()

    @property
    def refs(self) -> tuple[ContractReference[ApiSchema], ...]:
        return tuple(
            reference
            for branch in self.branches
            for reference in (branch.refs or ((branch.ref,) if branch.ref else ()))
        )

    @property
    def inline_branches(self) -> tuple[FrozenMap, ...]:
        return tuple(branch.inline for branch in self.branches if branch.inline)


@dataclass(frozen=True)
class NormalizedFieldView:
    api: ApiField
    source: SourceObject = field(default_factory=SourceObject)
    schema_use: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    item_use: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    constraints: NormalizedSchemaConstraints = field(
        default_factory=NormalizedSchemaConstraints
    )
    notes: StructuredNotes = field(default_factory=StructuredNotes)

    @property
    def id(self) -> str:
        return self.api.id

    @property
    def name(self) -> Any:
        return self.api.name


@dataclass(frozen=True)
class NormalizedSchemaView:
    api: ApiSchema
    source: SourceObject = field(default_factory=SourceObject)
    types: tuple[str, ...] = ()
    format: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    nullable: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    constraints: NormalizedSchemaConstraints = field(
        default_factory=NormalizedSchemaConstraints
    )
    fields: ContractCollection[NormalizedFieldView] = field(
        default_factory=ContractCollection
    )
    items: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    prefix_items: tuple[SchemaUse[ApiSchema], ...] = ()
    contains: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    additional_properties: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    property_names: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    pattern_properties: Mapping[str, SchemaUse[ApiSchema]] = field(
        default_factory=lambda: MappingProxyType({})
    )
    dependent_required: Mapping[str, tuple[str, ...]] = field(
        default_factory=lambda: MappingProxyType({})
    )
    dependent_schemas: Mapping[str, SchemaUse[ApiSchema]] = field(
        default_factory=lambda: MappingProxyType({})
    )
    compositions: tuple[NormalizedComposition, ...] = ()
    notes: StructuredNotes = field(default_factory=StructuredNotes)

    @property
    def id(self) -> str:
        return self.api.id

    @property
    def name(self) -> Any:
        return self.api.name

    @property
    def ref(self) -> str:
        return self.api.ref

    @property
    def kind(self) -> Any:
        return self.api.kind


@dataclass(frozen=True)
class NormalizedOperationView:
    api: ApiOperation
    source: SourceObject = field(default_factory=SourceObject)
    notes: StructuredNotes = field(default_factory=StructuredNotes)

    @property
    def id(self) -> str:
        return self.api.id

    @property
    def name(self) -> Any:
        return self.api.name


@dataclass(frozen=True)
class NormalizedResourceView:
    api: ApiResource
    source: SourceObject = field(default_factory=SourceObject)
    operations: ContractCollection[NormalizedOperationView] = field(
        default_factory=ContractCollection
    )
    schemas: ContractCollection[NormalizedSchemaView] = field(
        default_factory=ContractCollection
    )
    notes: StructuredNotes = field(default_factory=StructuredNotes)

    @property
    def id(self) -> str:
        return self.api.id

    @property
    def name(self) -> Any:
        return self.api.name


@dataclass(frozen=True)
class NormalizedApiView:
    source: SourceObject
    schemas: ContractCollection[NormalizedSchemaView] = field(
        default_factory=ContractCollection
    )
    operations: ContractCollection[NormalizedOperationView] = field(
        default_factory=ContractCollection
    )
    resources: ContractCollection[NormalizedResourceView] = field(
        default_factory=ContractCollection
    )
    diagnostics: tuple[ContractDiagnostic, ...] = ()
    raw_objects: Mapping[str, SourceObject] = field(
        default_factory=lambda: MappingProxyType({})
    )

    @property
    def all_diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        values = list(self.diagnostics)
        values.extend(self.source.diagnostics)
        for source in self.raw_objects.values():
            values.extend(source.diagnostics)
        for schema in self.schemas.all:
            values.extend(_schema_diagnostics(schema))
        return tuple(values)

    @property
    def loss_count(self) -> int:
        return sum(
            diagnostic.category == DiagnosticCategory.LOST
            for diagnostic in self.all_diagnostics
        )

    @property
    def unresolved_count(self) -> int:
        return sum(
            diagnostic.category == DiagnosticCategory.UNRESOLVED
            for diagnostic in self.all_diagnostics
        )

    @property
    def raw_only_count(self) -> int:
        return sum(
            diagnostic.category == DiagnosticCategory.RAW_ONLY
            for diagnostic in self.all_diagnostics
        )


def build_normalized_api_view(
    api: ApiContract,
    raw: Mapping[str, Any] | None,
) -> NormalizedApiView:
    document = _mapping(raw)
    schema_raw = _nested_mapping(document, "components", "schemas")
    path_raw = _mapping(document.get("paths"))
    codegen_raw = _mapping(document.get("x-codegen"))
    resource_raw = _mapping(codegen_raw.get("resources"))
    schema_targets = {schema.ref: schema for schema in api.schemas.all}

    normalized_schemas = tuple(
        _schema_view(
            schema,
            _mapping(schema_raw.get(schema.id)),
            schema_targets=schema_targets,
        )
        for schema in api.schemas.all
    )
    normalized_operations = tuple(
        _operation_view(operation, path_raw=path_raw) for operation in api.operations
    )
    normalized_resources = tuple(
        _resource_view(
            resource,
            _mapping(resource_raw.get(resource.id)),
            schemas=normalized_schemas,
            operations=normalized_operations,
        )
        for resource in api.resources
    )

    raw_objects: dict[str, SourceObject] = {
        **{f"schema:{schema.id}": schema.source for schema in normalized_schemas},
        **{
            f"operation:{operation.id}": operation.source
            for operation in normalized_operations
        },
        **{
            f"resource:{resource.id}": resource.source
            for resource in normalized_resources
        },
    }
    for schema in normalized_schemas:
        raw_objects.update(
            {
                f"schema:{schema.id}:field:{item.id}": item.source
                for item in schema.fields.all
            }
        )

    diagnostics = tuple(
        ContractDiagnostic(
            category=DiagnosticCategory.UNRESOLVED,
            level=DiagnosticLevel.WARNING,
            message=f"Internal schema ref is unresolved: {dependency.target_ref}",
            ref=dependency.target_ref,
            owner=dependency.source_ref,
        )
        for dependency in api.dependencies
        if dependency.target_ref not in schema_targets
    )
    return NormalizedApiView(
        source=source_object(
            document,
            source_path="$",
            known_keys={
                "openapi",
                "jsonSchemaDialect",
                "info",
                "servers",
                "paths",
                "webhooks",
                "components",
                "security",
                "tags",
                "externalDocs",
                "x-codegen",
            },
        ),
        schemas=contract_collection(
            normalized_schemas,
            classifiers={
                "models": lambda item: str(item.kind) == "model",
                "dtos": lambda item: str(item.kind) == "dto",
                "enums": lambda item: str(item.kind) == "enum",
                "primitives": lambda item: str(item.kind) == "primitive",
                "aliases": lambda item: item.api.is_alias,
            },
        ),
        operations=contract_collection(normalized_operations),
        resources=contract_collection(normalized_resources),
        diagnostics=diagnostics,
        raw_objects=MappingProxyType(raw_objects),
    )


def _schema_view(
    schema: ApiSchema,
    raw: Mapping[str, Any],
    *,
    schema_targets: Mapping[str, ApiSchema],
) -> NormalizedSchemaView:
    source_path = f"components.schemas.{schema.id}"
    properties = _mapping(raw.get("properties"))
    fields = tuple(
        _field_view(
            item,
            _mapping(properties.get(item.id)),
            owner=schema.ref,
            source_path=f"{source_path}.properties.{item.id}",
            schema_targets=schema_targets,
        )
        for item in schema.fields
    )
    return NormalizedSchemaView(
        api=schema,
        source=source_object(raw, source_path=source_path, known_keys=_SCHEMA_KEYS),
        types=_types(raw.get("type"), fallback=schema.primitive_type),
        format=presence_from_mapping(raw, "format", source_path=source_path),
        nullable=presence_from_mapping(raw, "nullable", source_path=source_path),
        constraints=_constraints(raw, source_path=source_path),
        fields=contract_collection(fields),
        items=_schema_use(
            raw.get("items"),
            owner=schema.ref,
            source_path=f"{source_path}.items",
            schema_targets=schema_targets,
        ),
        prefix_items=tuple(
            _schema_use(
                value,
                owner=schema.ref,
                source_path=f"{source_path}.prefixItems.{index}",
                schema_targets=schema_targets,
            )
            for index, value in enumerate(_sequence(raw.get("prefixItems")))
        ),
        contains=_schema_use(
            raw.get("contains"),
            owner=schema.ref,
            source_path=f"{source_path}.contains",
            schema_targets=schema_targets,
        ),
        additional_properties=presence_from_mapping(
            raw,
            "additionalProperties",
            source_path=source_path,
        ),
        property_names=_schema_use(
            raw.get("propertyNames"),
            owner=schema.ref,
            source_path=f"{source_path}.propertyNames",
            schema_targets=schema_targets,
        ),
        pattern_properties=MappingProxyType(
            {
                str(name): _schema_use(
                    value,
                    owner=schema.ref,
                    source_path=f"{source_path}.patternProperties.{name}",
                    schema_targets=schema_targets,
                )
                for name, value in _mapping(raw.get("patternProperties")).items()
            }
        ),
        dependent_required=MappingProxyType(
            {
                str(name): tuple(str(item) for item in _sequence(value))
                for name, value in _mapping(raw.get("dependentRequired")).items()
            }
        ),
        dependent_schemas=MappingProxyType(
            {
                str(name): _schema_use(
                    value,
                    owner=schema.ref,
                    source_path=f"{source_path}.dependentSchemas.{name}",
                    schema_targets=schema_targets,
                )
                for name, value in _mapping(raw.get("dependentSchemas")).items()
            }
        ),
        compositions=tuple(
            NormalizedComposition(
                kind=keyword,
                branches=tuple(
                    _schema_use(
                        value,
                        owner=schema.ref,
                        source_path=f"{source_path}.{keyword}.{index}",
                        schema_targets=schema_targets,
                    )
                    for index, value in enumerate(_sequence(raw.get(keyword)))
                ),
            )
            for keyword in ("allOf", "anyOf", "oneOf")
            if _sequence(raw.get(keyword))
        ),
        notes=structured_notes(
            _mapping(raw.get("x-codegen")).get(
                "info",
                _mapping(raw.get("x-codegen")).get("notes", raw.get("description")),
            )
        ),
    )


def _field_view(
    item: ApiField,
    raw: Mapping[str, Any],
    *,
    owner: str,
    source_path: str,
    schema_targets: Mapping[str, ApiSchema],
) -> NormalizedFieldView:
    return NormalizedFieldView(
        api=item,
        source=source_object(raw, source_path=source_path, known_keys=_SCHEMA_KEYS),
        schema_use=_schema_use(
            raw,
            owner=owner,
            source_path=source_path,
            schema_targets=schema_targets,
        ),
        item_use=_schema_use(
            _mapping(raw.get("items")),
            owner=owner,
            source_path=f"{source_path}.items",
            schema_targets=schema_targets,
        ),
        constraints=_constraints(raw, source_path=source_path),
        notes=structured_notes(
            _mapping(raw.get("x-codegen")).get("info", raw.get("description"))
        ),
    )


def _operation_view(
    operation: ApiOperation,
    *,
    path_raw: Mapping[str, Any],
) -> NormalizedOperationView:
    method = str(operation.method)
    raw = _mapping(_mapping(path_raw.get(operation.path)).get(method))
    source_path = f"paths.{operation.path}.{method}"
    return NormalizedOperationView(
        api=operation,
        source=source_object(raw, source_path=source_path, known_keys=_OPERATION_KEYS),
        notes=structured_notes(
            _mapping(raw.get("x-codegen")).get("info", raw.get("description"))
        ),
    )


def _resource_view(
    resource: ApiResource,
    raw: Mapping[str, Any],
    *,
    schemas: tuple[NormalizedSchemaView, ...],
    operations: tuple[NormalizedOperationView, ...],
) -> NormalizedResourceView:
    source_path = f"x-codegen.resources.{resource.id}"
    return NormalizedResourceView(
        api=resource,
        source=source_object(raw, source_path=source_path, known_keys=_RESOURCE_KEYS),
        operations=contract_collection(
            item for item in operations if item.api.resource == resource.id
        ),
        schemas=contract_collection(
            item for item in schemas if item.api.resource == resource.id
        ),
        notes=structured_notes(raw.get("info", raw.get("notes"))),
    )


def _constraints(
    raw: Mapping[str, Any],
    *,
    source_path: str,
) -> NormalizedSchemaConstraints:
    return NormalizedSchemaConstraints(
        **{
            attribute: presence_from_mapping(raw, key, source_path=source_path)
            for attribute, key in _CONSTRAINT_KEYS.items()
        }
    )


def _schema_use(
    value: Any,
    *,
    owner: str,
    source_path: str,
    schema_targets: Mapping[str, ApiSchema],
) -> SchemaUse[ApiSchema]:
    return build_schema_use(
        value,
        owner=owner,
        source_path=source_path,
        schema_targets=schema_targets,
    )


def _schema_diagnostics(schema: NormalizedSchemaView) -> tuple[ContractDiagnostic, ...]:
    values: list[ContractDiagnostic] = list(schema.source.diagnostics)
    for schema_use in (
        schema.items,
        schema.contains,
        schema.property_names,
        *schema.prefix_items,
        *schema.pattern_properties.values(),
        *schema.dependent_schemas.values(),
    ):
        values.extend(schema_use.diagnostics)
    for composition in schema.compositions:
        for branch in composition.branches:
            values.extend(branch.diagnostics)
    for item in schema.fields.all:
        values.extend(item.source.diagnostics)
        values.extend(item.schema_use.diagnostics)
        values.extend(item.item_use.diagnostics)
    return tuple(values)


def _types(value: Any, *, fallback: str | None) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list | tuple):
        return tuple(str(item) for item in value)
    return (fallback,) if fallback else ()


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _nested_mapping(value: Mapping[str, Any], *keys: str) -> Mapping[str, Any]:
    current: Any = value
    for key in keys:
        current = _mapping(current).get(key)
    return _mapping(current)


def _sequence(value: Any) -> tuple[Any, ...]:
    return tuple(value) if isinstance(value, list | tuple) else ()


_CONSTRAINT_KEYS = {
    "default": "default",
    "const": "const",
    "example": "example",
    "examples": "examples",
    "minimum": "minimum",
    "maximum": "maximum",
    "exclusive_minimum": "exclusiveMinimum",
    "exclusive_maximum": "exclusiveMaximum",
    "multiple_of": "multipleOf",
    "min_length": "minLength",
    "max_length": "maxLength",
    "pattern": "pattern",
    "content_encoding": "contentEncoding",
    "content_media_type": "contentMediaType",
    "min_items": "minItems",
    "max_items": "maxItems",
    "unique_items": "uniqueItems",
    "min_contains": "minContains",
    "max_contains": "maxContains",
    "min_properties": "minProperties",
    "max_properties": "maxProperties",
    "read_only": "readOnly",
    "write_only": "writeOnly",
    "deprecated": "deprecated",
}
_SCHEMA_KEYS = {
    "$ref",
    "$id",
    "$schema",
    "$anchor",
    "$dynamicRef",
    "$dynamicAnchor",
    "$defs",
    "type",
    "format",
    "nullable",
    "title",
    "description",
    "default",
    "const",
    "enum",
    "example",
    "examples",
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "multipleOf",
    "minLength",
    "maxLength",
    "pattern",
    "contentEncoding",
    "contentMediaType",
    "minItems",
    "maxItems",
    "uniqueItems",
    "minContains",
    "maxContains",
    "minProperties",
    "maxProperties",
    "readOnly",
    "writeOnly",
    "deprecated",
    "required",
    "properties",
    "additionalProperties",
    "patternProperties",
    "propertyNames",
    "dependentRequired",
    "dependentSchemas",
    "items",
    "prefixItems",
    "contains",
    "allOf",
    "anyOf",
    "oneOf",
    "not",
    "if",
    "then",
    "else",
    "discriminator",
    "xml",
    "externalDocs",
}
_OPERATION_KEYS = {
    "tags",
    "summary",
    "description",
    "externalDocs",
    "operationId",
    "parameters",
    "requestBody",
    "responses",
    "callbacks",
    "deprecated",
    "security",
    "servers",
    "x-codegen",
}
_RESOURCE_KEYS = {
    "name",
    "path",
    "route",
    "description",
    "info",
    "notes",
    "hooks",
    "access",
    "cache",
    "runtime",
}
