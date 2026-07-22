"""TypeScript schema template builders."""

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
from languages.typescript.dependencies import schema_dependencies
from languages.typescript.fields import template_field
from languages.typescript.names import TYPESCRIPT_RESERVED_WORDS, safe_enum_key
from languages.typescript.paths import resource_path_for_schema, safe_schema_file_name


def template_schema_groups(
    api: ApiContract,
    *,
    resource_paths: dict[str, tuple[str, ...]],
) -> TemplateSchemaGroups:
    """Build TypeScript schema groups."""
    schema_by_ref = {schema.ref: schema for schema in api.schemas.all}

    def build_group(
        schemas: tuple[ApiSchema, ...],
        group: TemplateGroup,
    ) -> tuple[TemplateSchema, ...]:
        return tuple(
            _schema(schema, group, schema_by_ref, resource_paths)
            for schema in schemas
        )

    return TemplateSchemaGroups(
        all=build_group(api.schemas.all, TemplateGroup.SCHEMAS),
        models=build_group(api.schemas.models, TemplateGroup.MODELS),
        dtos=build_group(api.schemas.dtos, TemplateGroup.DTOS),
        enums=build_group(api.schemas.enums, TemplateGroup.ENUMS),
        primitives=build_group(api.schemas.primitives, TemplateGroup.PRIMITIVES),
        aliases=build_group(api.schemas.aliases, TemplateGroup.ALIASES),
        unknown=build_group(api.schemas.unknown, TemplateGroup.UNKNOWN),
        queries=build_group(api.schemas.queries, TemplateGroup.QUERIES),
        params=build_group(api.schemas.params, TemplateGroup.PARAMS),
        bodies=build_group(api.schemas.bodies, TemplateGroup.BODIES),
        responses=build_group(api.schemas.responses, TemplateGroup.RESPONSES),
        emit_models=build_group(api.schemas.emit_models, TemplateGroup.MODELS),
        emit_dtos=build_group(api.schemas.emit_dtos, TemplateGroup.DTOS),
        emit_enums=build_group(api.schemas.emit_enums, TemplateGroup.ENUMS),
    )


def _schema(
    schema: ApiSchema,
    group: TemplateGroup,
    schema_by_ref: dict[str, ApiSchema],
    resource_paths: dict[str, tuple[str, ...]],
) -> TemplateSchema:
    base_schema = _base_schema(schema, schema_by_ref)

    if schema.has_field_overrides:
        api_fields = _merge_fields_with_overrides(schema, base_schema)
        fields = tuple(template_field(field, schema_by_ref) for field in api_fields)
        super_fields = ()
        extends_type = None
        has_extends = False
    else:
        own_fields = _own_api_fields(schema, base_schema)
        fields = tuple(template_field(field, schema_by_ref) for field in own_fields)
        super_fields = _super_fields(base_schema, schema_by_ref)
        extends_type = base_schema.name.pascal.o if base_schema else None
        has_extends = base_schema is not None

    dependencies = schema_dependencies(schema, schema_by_ref)
    resource_path = resource_path_for_schema(schema, resource_paths)
    file_name = safe_schema_file_name(schema)
    folder_path = _folder_path(schema=schema, group=group)

    return TemplateSchema(
        api=schema,
        name=schema.name,
        fields=fields,
        lang=TemplateSchemaLang(
            kind=f"typescript_{_schema_kind(schema)}",
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
                    safe_name=safe_enum_key(
                        value.value,
                        reserved_words=TYPESCRIPT_RESERVED_WORDS,
                    ),
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


def _merge_fields_with_overrides(
    schema: ApiSchema,
    base_schema: ApiSchema | None,
) -> tuple:
    """Merge base and child fields, with child fields overriding base fields."""
    if base_schema is None:
        return schema.fields

    merged = {field.name.camel.o: field for field in base_schema.fields}
    merged.update({field.name.camel.o: field for field in schema.fields})
    return tuple(merged.values())


def _own_api_fields(
    schema: ApiSchema,
    base_schema: ApiSchema | None,
) -> tuple:
    if base_schema is None:
        return schema.fields

    inherited = {field.name.camel.o for field in base_schema.fields}
    return tuple(field for field in schema.fields if field.name.camel.o not in inherited)


def _super_fields(
    base_schema: ApiSchema | None,
    schema_by_ref: dict[str, ApiSchema],
) -> tuple[TemplateField, ...]:
    if base_schema is None:
        return ()

    return tuple(template_field(field, schema_by_ref) for field in base_schema.fields)


def _folder_path(
    *,
    schema: ApiSchema,
    group: TemplateGroup,
) -> tuple[str, ...]:
    if group == TemplateGroup.ENUMS:
        return (schema.name.path.o,)

    if group == TemplateGroup.DTOS:
        return (_dto_operation(schema), _dto_role(schema))

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
