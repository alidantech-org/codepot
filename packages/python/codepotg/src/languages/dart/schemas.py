"""Dart schema template builders."""

from __future__ import annotations

from contracts.api import ApiContract, ApiSchema, ApiSchemaKind
from contracts.template import (
    TemplateDocs,
    TemplateEnumValue,
    TemplateField,
    TemplateGroup,
    TemplateItemEmit,
    TemplateItemKey,
    TemplateSchema,
    TemplateSchemaGroups,
    TemplateSchemaLang,
    TemplateSchemaMeta,
)
from languages.dart.dependencies import schema_dependencies
from languages.dart.fields import template_field
from languages.dart.names import DART_RESERVED_WORDS, safe_enum_key
from languages.dart.paths import resource_path_for_schema, safe_schema_file_name


def _merge_fields_with_overrides(
    schema: ApiSchema,
    base_schema: ApiSchema | None,
    schema_by_ref: dict[str, ApiSchema],
) -> tuple:
    """Merge base and child fields, with child fields overriding base fields."""
    if base_schema is None:
        return schema.fields

    # Build dict of inherited fields by wire name, including the full ancestor chain.
    base_fields_by_wire = {
        field.name.camel.o: field
        for field in _constructor_api_fields(base_schema, schema_by_ref)
    }

    # Build dict of child fields by wire name (child wins)
    child_fields_by_wire = {field.name.camel.o: field for field in schema.fields}

    # Merge: start with base, override with child
    merged_fields = base_fields_by_wire.copy()
    merged_fields.update(child_fields_by_wire)

    return tuple(merged_fields.values())


def _base_schema(
    schema: ApiSchema,
    schema_by_ref: dict[str, ApiSchema],
) -> ApiSchema | None:
    if schema.inherited_refs:
        return schema_by_ref.get(schema.inherited_refs[0])

    if schema.alias_of:
        target = schema_by_ref.get(schema.alias_of)
        if target and target.kind in {ApiSchemaKind.MODEL, ApiSchemaKind.DTO}:
            return target

    return None


def _own_api_fields(
    schema: ApiSchema,
    base_schema: ApiSchema | None,
    schema_by_ref: dict[str, ApiSchema],
) -> tuple:
    if base_schema is None:
        return schema.fields

    inherited = {
        field.name.camel.o
        for field in _constructor_api_fields(base_schema, schema_by_ref)
    }
    return tuple(field for field in schema.fields if field.name.camel.o not in inherited)


def _super_fields(
    base_schema: ApiSchema | None,
    schema_by_ref: dict[str, ApiSchema],
) -> tuple[TemplateField, ...]:
    if base_schema is None:
        return ()

    return tuple(
        template_field(field, schema_by_ref)
        for field in _constructor_api_fields(base_schema, schema_by_ref)
    )


def _constructor_api_fields(
    schema: ApiSchema,
    schema_by_ref: dict[str, ApiSchema],
    seen_refs: frozenset[str] = frozenset(),
) -> tuple:
    """Return fields accepted by this schema's generated constructor."""
    if schema.ref in seen_refs:
        return schema.fields

    base_schema = _base_schema(schema, schema_by_ref)
    if base_schema is None or schema.has_field_overrides:
        return schema.fields

    inherited_fields = _constructor_api_fields(base_schema, schema_by_ref, seen_refs | {schema.ref})
    inherited_names = {field.name.camel.o for field in inherited_fields}
    own_fields = tuple(
        field for field in schema.fields if field.name.camel.o not in inherited_names
    )

    return (*inherited_fields, *own_fields)


def template_schema_groups(
    api: ApiContract,
    *,
    resource_paths: dict[str, tuple[str, ...]],
) -> TemplateSchemaGroups:
    """Build Dart schema groups."""
    schema_by_ref = {schema.ref: schema for schema in api.schemas.all}

    return TemplateSchemaGroups(
        all=tuple(_schema(schema, TemplateGroup.SCHEMAS, schema_by_ref, resource_paths) for schema in api.schemas.all),
        models=tuple(_schema(schema, TemplateGroup.MODELS, schema_by_ref, resource_paths) for schema in api.schemas.models),
        dtos=tuple(_schema(schema, TemplateGroup.DTOS, schema_by_ref, resource_paths) for schema in api.schemas.dtos),
        enums=tuple(_schema(schema, TemplateGroup.ENUMS, schema_by_ref, resource_paths) for schema in api.schemas.enums),
        primitives=tuple(_schema(schema, TemplateGroup.PRIMITIVES, schema_by_ref, resource_paths) for schema in api.schemas.primitives),
        aliases=tuple(_schema(schema, TemplateGroup.ALIASES, schema_by_ref, resource_paths) for schema in api.schemas.aliases),
        unknown=tuple(_schema(schema, TemplateGroup.UNKNOWN, schema_by_ref, resource_paths) for schema in api.schemas.unknown),
        queries=tuple(_schema(schema, TemplateGroup.QUERIES, schema_by_ref, resource_paths) for schema in api.schemas.queries),
        params=tuple(_schema(schema, TemplateGroup.PARAMS, schema_by_ref, resource_paths) for schema in api.schemas.params),
        bodies=tuple(_schema(schema, TemplateGroup.BODIES, schema_by_ref, resource_paths) for schema in api.schemas.bodies),
        responses=tuple(_schema(schema, TemplateGroup.RESPONSES, schema_by_ref, resource_paths) for schema in api.schemas.responses),
        emit_models=tuple(_schema(schema, TemplateGroup.MODELS, schema_by_ref, resource_paths) for schema in api.schemas.emit_models),
        emit_dtos=tuple(_schema(schema, TemplateGroup.DTOS, schema_by_ref, resource_paths) for schema in api.schemas.emit_dtos),
        emit_enums=tuple(_schema(schema, TemplateGroup.ENUMS, schema_by_ref, resource_paths) for schema in api.schemas.emit_enums),
    )


def _schema(
    schema: ApiSchema,
    group: TemplateGroup,
    schema_by_ref: dict[str, ApiSchema],
    resource_paths: dict[str, tuple[str, ...]],
) -> TemplateSchema:
    base_schema = _base_schema(schema, schema_by_ref)

    # If has field overrides, use flattened composition with merged fields
    if schema.has_field_overrides:
        merged_fields = _merge_fields_with_overrides(schema, base_schema, schema_by_ref)
        fields = tuple(template_field(field, schema_by_ref) for field in merged_fields)
        super_fields = ()
        extends_type = None
        has_extends = False
    else:
        own_api_fields = _own_api_fields(schema, base_schema, schema_by_ref)
        fields = tuple(template_field(field, schema_by_ref) for field in own_api_fields)
        super_fields = _super_fields(base_schema, schema_by_ref)
        extends_type = base_schema.name.pascal.o if base_schema else None
        has_extends = base_schema is not None

    dependencies = schema_dependencies(schema, schema_by_ref)
    resource_path = resource_path_for_schema(schema, resource_paths)
    file_name = safe_schema_file_name(schema)
    folder_path = _folder_path(schema=schema, group=group, resource_path=resource_path)

    return TemplateSchema(
        api=schema,
        name=schema.name,
        fields=fields,
        lang=TemplateSchemaLang(
            kind=f"dart_{_schema_kind(schema)}",
            type=_schema_kind(schema),
            display_name=schema.name.pascal.o,
            symbol_name=schema.name.pascal.o,
            field_count=len(fields),
            dependency_count=len(dependencies),
            query_enabled=schema.query.enabled,
        ),
        emit=TemplateItemEmit(
            group=group,
            item_key=_item_key(group),
            key=schema.ref,
            ref=schema.ref,
            path_parts=(group.value, schema.name.path.o),
            path=folder_path,
            resource_path=resource_path,
            folder_path=folder_path,
            file_name=file_name,
            relative_doc_path=folder_path,
            dependency_refs=schema.dependencies,
            dependencies=dependencies,
            imports=tuple(dependency for dependency in dependencies if dependency.is_importable),
        ),
        docs=TemplateDocs(description=schema.description),
        meta=TemplateSchemaMeta(
            is_alias=schema.is_alias,
            alias_of=schema.alias_of,
            primitive_type=schema.primitive_type,
            primitive_format=schema.primitive_format,
            enum_type=schema.enum_type,
            enum_values=tuple(
                TemplateEnumValue(
                    wire=value.value,
                    name=value.name.camel.o,
                    safe_name=safe_enum_key(value.value, reserved_words=DART_RESERVED_WORDS),
                    original_name=value.value,
                )
                for value in schema.enum_values
            ),
            enum_count=len(schema.enum_values),
            composition_refs=schema.composition_refs,
            inherited_refs=schema.inherited_refs,
            query_enabled=schema.query.enabled,
            has_extends=has_extends,
            extends_type=extends_type,
            super_fields=super_fields,
        ),
    )


def _folder_path(
    *,
    schema: ApiSchema,
    group: TemplateGroup,
    resource_path: tuple[str, ...],
) -> tuple[str, ...]:
    if group == TemplateGroup.ENUMS:
        return (schema.name.path.o,)

    if group == TemplateGroup.DTOS:
        role = _dto_role(schema)
        operation = _dto_operation(schema)
        return (operation, role)

    return (schema.name.path.o,)


def _dto_role(schema: ApiSchema) -> str:
    role = schema.meta.get("role") or schema.meta.get("dto_role")
    if isinstance(role, str) and role:
        return role

    roles = schema.meta.get("roles")
    if isinstance(roles, (list, tuple)) and roles and isinstance(roles[0], str):
        return roles[0]

    return "model"


def _dto_operation(schema: ApiSchema) -> str:
    operation = schema.meta.get("operation") or schema.meta.get("operation_name")
    if isinstance(operation, str) and operation:
        return operation

    return schema.name.path.o


def _schema_kind(schema: ApiSchema) -> str:
    return schema.kind.value if hasattr(schema.kind, "value") else str(schema.kind)


def _item_key(group: TemplateGroup) -> TemplateItemKey:
    if group == TemplateGroup.MODELS:
        return TemplateItemKey.MODEL

    if group == TemplateGroup.DTOS:
        return TemplateItemKey.DTO

    if group == TemplateGroup.ENUMS:
        return TemplateItemKey.ENUM

    if group == TemplateGroup.PRIMITIVES:
        return TemplateItemKey.PRIMITIVE

    return TemplateItemKey.SCHEMA
