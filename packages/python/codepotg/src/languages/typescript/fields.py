"""TypeScript field template builders."""

from __future__ import annotations

from contracts.api import ApiField, ApiSchema, ApiSchemaKind
from contracts.template import (
    TemplateEnumValue,
    TemplateField,
    TemplateFieldLang,
    TemplateFieldMeta,
    TemplateGroup,
    TemplateItemEmit,
    TemplateItemKey,
)
from languages.typescript.dependencies import field_dependencies
from languages.typescript.names import TYPESCRIPT_RESERVED_WORDS, safe_enum_key
from languages.typescript.types import ts_field_type


def _ts_nullable(field: ApiField, schema_by_ref: dict[str, ApiSchema]) -> bool:
    """Return whether the TypeScript field type includes null."""
    if field.nullable:
        return True

    ref_schema = schema_by_ref.get(field.schema_ref or "")
    return bool(ref_schema and ref_schema.nullable)


def _ts_optional(field: ApiField) -> bool:
    """Return whether the TypeScript field should be optional."""
    return not field.required


def template_field(
    field: ApiField,
    schema_by_ref: dict[str, ApiSchema],
) -> TemplateField:
    """Build a TemplateField for TypeScript templates."""
    dependencies = field_dependencies(field, schema_by_ref)

    return TemplateField(
        api=field,
        name=field.name,
        lang=TemplateFieldLang(
            kind="typescript_field",
            type=ts_field_type(field, schema_by_ref),
            display_name=field.name.camel.o,
            required=field.required,
            nullable=_ts_nullable(field, schema_by_ref),
            # optional=_ts_optional(field),
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
            enum_options=_field_enum_options(field, schema_by_ref),
            enum_type=_field_enum_type(field, schema_by_ref),
            enum_ref=_field_enum_ref(field, schema_by_ref),
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


def _field_enum_options(
    field: ApiField,
    schema_by_ref: dict[str, ApiSchema],
) -> tuple[TemplateEnumValue, ...]:
    schema = _field_enum_schema(field, schema_by_ref)
    if schema is not None:
        return tuple(
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
        )

    return tuple(
        TemplateEnumValue(
            wire=value,
            name=safe_enum_key(value, reserved_words=TYPESCRIPT_RESERVED_WORDS),
            safe_name=safe_enum_key(value, reserved_words=TYPESCRIPT_RESERVED_WORDS),
            original_name=value,
        )
        for value in field.enum_values
    )


def _field_enum_type(
    field: ApiField,
    schema_by_ref: dict[str, ApiSchema],
) -> str | None:
    schema = _field_enum_schema(field, schema_by_ref)
    if schema is not None:
        return schema.name.pascal.o

    if field.enum_values:
        return field.type.type

    return None


def _field_enum_ref(
    field: ApiField,
    schema_by_ref: dict[str, ApiSchema],
) -> str | None:
    schema = _field_enum_schema(field, schema_by_ref)
    return schema.ref if schema is not None else None


def _field_enum_schema(
    field: ApiField,
    schema_by_ref: dict[str, ApiSchema],
) -> ApiSchema | None:
    for ref in (
        field.schema_ref,
        *field.schema_refs,
        field.item_ref,
        *field.item_refs,
    ):
        schema = schema_by_ref.get(ref or "")
        if schema is not None and _kind_value(schema.kind) == ApiSchemaKind.ENUM.value:
            return schema

    return None


def _kind_value(value: object) -> str:
    enum_value = getattr(value, "value", None)
    if isinstance(enum_value, str):
        return enum_value

    if isinstance(value, str):
        return value

    return ""
