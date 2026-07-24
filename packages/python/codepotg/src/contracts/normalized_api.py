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
    ReferenceKind,
    ResolutionState,
    SchemaUse,
    SchemaUseKind,
    SourceObject,
    StructuredNotes,
    contract_collection,
    presence_from_mapping,
    source_object,
    structured_notes,
)
from contracts.source import FrozenMap, freeze_source_map


@dataclass(frozen=True)
class NormalizedSchemaConstraints:
    """Presence-aware JSON Schema values and validation constraints."""

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
    """Reference and inline branches for one schema composition keyword."""

    kind: str
    branches: tuple[SchemaUse[ApiSchema], ...] = ()

    @property
    def refs(self) -> tuple[ContractReference[ApiSchema], ...]:
        return tuple(
            reference
            for branch in self.branches
            for reference in branch.refs
        )

    @property
    def inline_branches(self) -> tuple[FrozenMap, ...]:
        return tuple(branch.inline for branch in self.branches if branch.inline)


@dataclass(frozen=True)
class NormalizedFieldView:
    """Additive normalized view of one schema field."""

    api: ApiField
    source: SourceObject = field(default_factory=SourceObject)
    schema_use: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    item_use: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    constraints: NormalizedSchemaConstraints = field(default_factory=NormalizedSchemaConstraints)
    notes: StructuredNotes = field(default_factory=StructuredNotes)

    @property
    def id(self) -> str:
        return self.api.id

    @property
    def name(self) -> Any:
        return self.api.name


@dataclass(frozen=True)
class NormalizedSchemaView:
    """Additive normalized and lossless schema view."""

    api: ApiSchema
    source: SourceObject = field(default_factory=SourceObject)
    types: tuple[str, ...] = ()
    format: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    nullable: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    constraints: NormalizedSchemaConstraints = field(default_factory=NormalizedSchemaConstraints)
    fields: ContractCollection[NormalizedFieldView] = field(default_factory=ContractCollection)
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
    """Lossless operation source plus existing typed operation facts."""

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
    """Lossless resource source plus linked typed collections."""

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
    """Parallel migration root for lossless normalized template facts."""

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
    def loss_count(self) -> int:
        return sum(
            1
            for diagnostic in self.all_diagnostics
            if diagnostic.category == DiagnosticCategory.LOST
        )

    @property
    def unresolved_count(self) -> int:
        return sum(
            1
            for diagnostic in self.all_diagnostics
            if diagnostic.category == DiagnosticCategory.UNRESOLVED
        )

    @property
    def raw_only_count(self) -> int:
        return sum(
            1
            for diagnostic in self.all_diagnostics
            if diagnostic.category == DiagnosticCategory.RAW_ONLY
        )

    @property
    def all_diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        values = list(self.diagnostics)
        values.extend(self.source.diagnostics)
        for source in self.raw_objects.values():
            values.extend(source.diagnostics)
        return tuple(values)


def build_normalized_api_view(
    api: ApiContract,
    raw: Mapping[str, Any] | None,
) -> NormalizedApiView:
    """Build a lossless additive view without replacing compatibility fields."""

    document = raw or {}
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
    schema_views_by_id = {schema.id: schema for schema in normalized_schemas}

    normalized_operations = tuple(
        _operation_view(operation, path_raw=path_raw)
        for operation in api.operations
    )
    operation_views_by_id = {
        operation.id: operation for operation in normalized_operations
    }

    normalized_resources = tuple(
        _resource_view(
            resource,
            _mapping(resource_raw.get(resource.id)),
            schemas=normalized_schemas,
            operations=normalized_operations,
        )
        for resource in api.resources
    )

    raw_objects: dict[str, SourceObject] = {}
    raw_objects.update(
        {f"schema:{schema.id}": schema.source for schema in normalized_schemas}
    )
    for schema in normalized_schemas:
        raw_objects.update(
            {
                f"schema:{schema.id}:field:{field.id}": field.source
                for field in schema.fields.all
            }
        )
    raw_objects.update(
        {
            f"operation:{operation.id}": operation.source
            for operation in normalized_operations
        }
    )
    raw_objects.update(
        {
            f"resource:{resource.id}": resource.source
            for resource in normalized_resources
        }
    )

    diagnostics: list[ContractDiagnostic] = []
    for dependency in api.dependencies:
        if dependency.target_ref not in schema_targets:
            diagnostics.append(
                ContractDiagnostic(
                    category=DiagnosticCategory.UNRESOLVED,
                    level=DiagnosticLevel.WARNING,
                    message=f"Internal schema ref is unresolved: {dependency.target_ref}",
                    ref=dependency.target_ref,
                    owner=dependency.source_ref,
                )
            )

    source = source_object(
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
    )
    return NormalizedApiView(
        source=source,
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
        diagnostics=tuple(diagnostics),
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
            field,
            _mapping(properties.get(field.id)),
            owner_ref=schema.ref,
            schema_targets=schema_targets,
        )
        for field in schema.fields
    )
    types = _types(raw.get("type"), fallback=schema.primitive_type)
    x_codegen = _mapping(raw.get("x-codegen"))
    notes = structured_notes(
        x_codegen.get("info", x_codegen.get("notes", raw.get("description")))
    )
    return NormalizedSchemaView(
        api=schema,
        source=source_object(
            raw,
            source_path=source_path,
            known_keys=_SCHEMA_KNOWN_KEYS,
        ),
        types=types,
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
                str(pattern): _schema_use(
                    value,
                    owner=schema.ref,
                    source_path=f"{source_path}.patternProperties.{pattern}",
                    schema_targets=schema_targets,
                )
                for pattern, value in _mapping(raw.get("patternProperties")).items()
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
            _composition(
                kind,
                raw.get(kind),
                owner=schema.ref,
                source_path=f"{source_path}.{kind}",
                schema_targets=schema_targets,
            )
            for kind in ("allOf", "anyOf", "oneOf", "not", "if", "then", "else")
            if kind in raw
        ),
        notes=notes,
    )


def _field_view(
    field_value: ApiField,
    raw: Mapping[str, Any],
    *,
    owner_ref: str,
    schema_targets: Mapping[str, ApiSchema],
) -> NormalizedFieldView:
    source_path = f"{owner_ref}.properties.{field_value.id}"
    x_codegen = _mapping(raw.get("x-codegen"))
    return NormalizedFieldView(
        api=field_value,
        source=source_object(
            raw,
            source_path=source_path,
            known_keys=_SCHEMA_KNOWN_KEYS,
        ),
        schema_use=_schema_use(
            raw,
            owner=owner_ref,
            source_path=source_path,
            schema_targets=schema_targets,
        ),
        item_use=_schema_use(
            raw.get("items"),
            owner=owner_ref,
            source_path=f"{source_path}.items",
            schema_targets=schema_targets,
        ),
        constraints=_constraints(raw, source_path=source_path),
        notes=structured_notes(
            x_codegen.get("info", x_codegen.get("notes", raw.get("description")))
        ),
    )


def _operation_view(
    operation: ApiOperation,
    *,
    path_raw: Mapping[str, Any],
) -> NormalizedOperationView:
    path_item = _mapping(path_raw.get(operation.path))
    raw = _mapping(path_item.get(str(operation.method)))
    source_path = f"paths.{operation.path}.{operation.method}"
    x_codegen = _mapping(raw.get("x-codegen"))
    return NormalizedOperationView(
        api=operation,
        source=source_object(
            raw,
            source_path=source_path,
            known_keys=_OPERATION_KNOWN_KEYS,
        ),
        notes=structured_notes(
            x_codegen.get("info", x_codegen.get("notes", raw.get("description")))
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
    selected_schemas = tuple(
        schema for schema in schemas if schema.api.resource == resource.id
    )
    selected_operations = tuple(
        operation for operation in operations if operation.api.resource == resource.id
    )
    return NormalizedResourceView(
        api=resource,
        source=source_object(
            raw,
            source_path=source_path,
            known_keys={
                "name",
                "path",
                "route",
                "tags",
                "ui",
                "access",
                "hooks",
                "info",
                "notes",
            },
        ),
        operations=contract_collection(selected_operations),
        schemas=contract_collection(selected_schemas),
        notes=structured_notes(raw.get("info", raw.get("notes"))),
    )


def _constraints(
    raw: Mapping[str, Any],
    *,
    source_path: str,
) -> NormalizedSchemaConstraints:
    return NormalizedSchemaConstraints(
        default=presence_from_mapping(raw, "default", source_path=source_path),
        const=presence_from_mapping(raw, "const", source_path=source_path),
        example=presence_from_mapping(raw, "example", source_path=source_path),
        examples=presence_from_mapping(raw, "examples", source_path=source_path),
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
        min_items=presence_from_mapping(raw, "minItems", source_path=source_path),
        max_items=presence_from_mapping(raw, "maxItems", source_path=source_path),
        unique_items=presence_from_mapping(
            raw, "uniqueItems", source_path=source_path
        ),
        min_contains=presence_from_mapping(
            raw, "minContains", source_path=source_path
        ),
        max_contains=presence_from_mapping(
            raw, "maxContains", source_path=source_path
        ),
        min_properties=presence_from_mapping(
            raw, "minProperties", source_path=source_path
        ),
        max_properties=presence_from_mapping(
            raw, "maxProperties", source_path=source_path
        ),
        read_only=presence_from_mapping(raw, "readOnly", source_path=source_path),
        write_only=presence_from_mapping(raw, "writeOnly", source_path=source_path),
        deprecated=presence_from_mapping(raw, "deprecated", source_path=source_path),
    )


def _composition(
    kind: str,
    value: Any,
    *,
    owner: str,
    source_path: str,
    schema_targets: Mapping[str, ApiSchema],
) -> NormalizedComposition:
    values = _sequence(value) if kind in {"allOf", "anyOf", "oneOf"} else (value,)
    return NormalizedComposition(
        kind=kind,
        branches=tuple(
            _schema_use(
                branch,
                owner=owner,
                source_path=f"{source_path}.{index}",
                schema_targets=schema_targets,
            )
            for index, branch in enumerate(values)
        ),
    )


def _schema_use(
    value: Any,
    *,
    owner: str,
    source_path: str,
    schema_targets: Mapping[str, ApiSchema],
) -> SchemaUse[ApiSchema]:
    raw = _mapping(value)
    if not raw:
        return SchemaUse(source_path=source_path)
    refs = tuple(
        _reference(
            ref,
            owner=owner,
            source_path=source_path,
            schema_targets=schema_targets,
        )
        for ref in _direct_refs(raw)
    )
    primary = refs[0] if refs else None
    inline_keys = {key: item for key, item in raw.items() if key != "$ref"}
    inline = freeze_source_map(inline_keys) if inline_keys else FrozenMap()
    resolved_targets = tuple(
        reference.target for reference in refs if reference.target is not None
    )
    schema = resolved_targets[0] if len(resolved_targets) == 1 else None
    if refs and inline:
        kind = SchemaUseKind.MIXED
    elif len(refs) > 1:
        kind = SchemaUseKind.MULTIPLE_REFERENCES
    elif refs:
        kind = SchemaUseKind.REFERENCE
    elif inline:
        kind = SchemaUseKind.INLINE
    else:
        kind = SchemaUseKind.EMPTY
    return SchemaUse(
        kind=kind,
        ref=primary,
        refs=refs,
        schema=schema,
        inline=inline,
        source_path=source_path,
        diagnostics=tuple(
            diagnostic
            for reference in refs
            for diagnostic in reference.diagnostics
        ),
    )


def _reference(
    ref: str,
    *,
    owner: str,
    source_path: str,
    schema_targets: Mapping[str, ApiSchema],
) -> ContractReference[ApiSchema]:
    target = schema_targets.get(ref)
    if target is not None:
        return ContractReference(
            ref=ref,
            kind=ReferenceKind.SCHEMA,
            name=target.id,
            owner=owner,
            state=ResolutionState.RESOLVED,
            target=target,
            source_path=source_path,
        )
    if not ref.startswith("#/"):
        return ContractReference(
            ref=ref,
            kind=ReferenceKind.SCHEMA,
            owner=owner,
            state=ResolutionState.EXTERNAL,
            source_path=source_path,
        )
    diagnostic = ContractDiagnostic(
        category=DiagnosticCategory.UNRESOLVED,
        level=DiagnosticLevel.WARNING,
        message=f"Internal schema ref is unresolved: {ref}",
        source_path=source_path,
        ref=ref,
        owner=owner,
    )
    return ContractReference(
        ref=ref,
        kind=ReferenceKind.SCHEMA,
        owner=owner,
        state=ResolutionState.MISSING,
        source_path=source_path,
        diagnostics=(diagnostic,),
    )


def _direct_refs(value: Mapping[str, Any]) -> tuple[str, ...]:
    refs: list[str] = []
    direct = value.get("$ref")
    if isinstance(direct, str):
        refs.append(direct)
    for keyword in ("allOf", "anyOf", "oneOf"):
        for branch in _sequence(value.get(keyword)):
            if isinstance(branch, Mapping):
                ref = branch.get("$ref")
                if isinstance(ref, str):
                    refs.append(ref)
    return tuple(dict.fromkeys(refs))


def _types(value: Any, *, fallback: str | None) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list | tuple):
        return tuple(str(item) for item in value)
    return (fallback,) if fallback else ()


def _nested_mapping(source: Mapping[str, Any], *keys: str) -> Mapping[str, Any]:
    current: Any = source
    for key in keys:
        current = _mapping(current).get(key)
    return _mapping(current)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> tuple[Any, ...]:
    if isinstance(value, list | tuple):
        return tuple(value)
    return ()


_SCHEMA_KNOWN_KEYS = {
    "$ref",
    "$id",
    "$schema",
    "$anchor",
    "$dynamicAnchor",
    "$dynamicRef",
    "title",
    "summary",
    "description",
    "type",
    "format",
    "nullable",
    "enum",
    "default",
    "const",
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
    "contentSchema",
    "items",
    "prefixItems",
    "contains",
    "minContains",
    "maxContains",
    "minItems",
    "maxItems",
    "uniqueItems",
    "unevaluatedItems",
    "properties",
    "required",
    "additionalProperties",
    "patternProperties",
    "propertyNames",
    "minProperties",
    "maxProperties",
    "dependentRequired",
    "dependentSchemas",
    "unevaluatedProperties",
    "allOf",
    "anyOf",
    "oneOf",
    "not",
    "if",
    "then",
    "else",
    "discriminator",
    "readOnly",
    "writeOnly",
    "deprecated",
    "externalDocs",
    "xml",
    "x-codegen",
}
_OPERATION_KNOWN_KEYS = {
    "operationId",
    "summary",
    "description",
    "tags",
    "parameters",
    "requestBody",
    "responses",
    "callbacks",
    "deprecated",
    "security",
    "servers",
    "externalDocs",
    "x-codegen",
}
