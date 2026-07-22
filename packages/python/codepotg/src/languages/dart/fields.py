"""Dart field template builders."""

from __future__ import annotations

from contracts.api import ApiField, ApiSchema
from contracts.template import (
    TemplateField,
    TemplateFieldLang,
    TemplateFieldMeta,
    TemplateGroup,
    TemplateItemEmit,
    TemplateItemKey,
)
from languages.dart.dependencies import field_dependencies
from languages.dart.names import safe_dart_identifier
from languages.dart.types import dart_field_type


def _dart_nullable(field: ApiField, schema_by_ref: dict[str, ApiSchema]) -> bool:
    """Return whether the Dart field type must be nullable."""
    if not field.required:
        return True

    if field.nullable:
        return True

    ref_schema = schema_by_ref.get(field.schema_ref or "")
    return bool(ref_schema and ref_schema.nullable)


def template_field(
    field: ApiField,
    schema_by_ref: dict[str, ApiSchema],
) -> TemplateField:
    """Build a TemplateField for Dart templates."""
    dependencies = field_dependencies(field, schema_by_ref)
    display_name = safe_dart_identifier(field.name.camel.original, fallback="field")
    wire_name = field.name.camel.o
    json_key = wire_name if display_name != wire_name else None

    return TemplateField(
        api=field,
        name=field.name,
        lang=TemplateFieldLang(
            kind="dart_field",
            type=dart_field_type(field, schema_by_ref),
            display_name=display_name,
            json_key=json_key,
            required=field.required,
            nullable=_dart_nullable(field, schema_by_ref),
            query_enabled=field.query.enabled,
            sortable=field.query.sortable,
            selectable=field.query.selectable,
            filterable=field.query.filterable,
            searchable=field.query.searchable,
            operators=field.query.operators,
        ),
        emit=TemplateItemEmit(
            group=TemplateGroup.FIELDS,
            item_key=TemplateItemKey.FIELD,
            key=field.id,
            ref=field.schema_ref,
            path_parts=(TemplateGroup.FIELDS.value, field.name.path.o),
            dependency_refs=_field_dependency_refs(field),
            dependencies=dependencies,
        ),
        meta=TemplateFieldMeta(
            default=field.default,
            enum_values=field.enum_values,
            raw_type=field.type.raw_type,
        ),
    )


def _field_dependency_refs(field: ApiField) -> tuple[str, ...]:
    refs: list[str] = []

    for ref in (
        field.schema_ref,
        *field.schema_refs,
        field.item_ref,
        *field.item_refs,
    ):
        if ref and ref not in refs:
            refs.append(ref)

    return tuple(refs)
