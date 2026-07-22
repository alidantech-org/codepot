"""Dart type mapping helpers."""

from __future__ import annotations

from contracts.api import ApiField, ApiFieldKind, ApiSchema, ApiSchemaKind
from contracts.template import TemplateDependencyTargetKind

_OPENAPI_PRIMITIVES = {"string", "integer", "number", "boolean", "object"}
_DATE_FORMATS = {"date", "date-time"}


def dart_field_type(
    field: ApiField,
    schema_by_ref: dict[str, ApiSchema],
) -> str:
    """Return the Dart type label for a field."""
    base = _dart_base_type(field, schema_by_ref)

    if base == "dynamic":
        return "dynamic"

    if _field_is_dart_nullable(field, schema_by_ref):
        return f"{base}?"

    return base


def dependency_is_generated_import(kind: TemplateDependencyTargetKind) -> bool:
    """Return whether a dependency target should be imported in Dart."""
    return kind in {
        TemplateDependencyTargetKind.ENUM,
        TemplateDependencyTargetKind.MODEL,
        TemplateDependencyTargetKind.DTO,
    }


def _field_is_dart_nullable(
    field: ApiField,
    schema_by_ref: dict[str, ApiSchema],
) -> bool:
    """Return whether the Dart field type must be nullable."""
    if not field.required or field.nullable:
        return True

    for ref in _field_schema_refs(field):
        schema = schema_by_ref.get(ref)
        if schema is not None and _schema_is_nullable(schema):
            return True

    return False


def _dart_base_type(
    field: ApiField,
    schema_by_ref: dict[str, ApiSchema],
) -> str:
    kind = _kind_value(field.type.kind)

    if kind == ApiFieldKind.ARRAY.value:
        return f"List<{_dart_array_item_type(field, schema_by_ref)}>"

    ref_type = _first_schema_ref_type(_field_schema_refs(field), schema_by_ref)
    if ref_type is not None:
        return ref_type

    if kind == ApiFieldKind.PRIMITIVE.value:
        return _dart_primitive_type(field.type.type, field.type.format)

    if kind == ApiFieldKind.OBJECT.value:
        return "Map<String, dynamic>"

    if kind in {
        ApiFieldKind.ENUM.value,
        ApiFieldKind.MODEL.value,
        ApiFieldKind.DTO.value,
    }:
        return _safe_named_or_primitive_type(field.type.type, field.type.format)

    return _fallback_type(field)


def _dart_array_item_type(
    field: ApiField,
    schema_by_ref: dict[str, ApiSchema],
) -> str:
    ref_type = _first_schema_ref_type(_field_item_refs(field), schema_by_ref)
    if ref_type is not None:
        return ref_type

    item_kind = _kind_value(field.type.item_kind)

    if item_kind == ApiFieldKind.PRIMITIVE.value:
        return _dart_primitive_type(field.type.item_type, field.type.item_format)

    if item_kind in {
        ApiFieldKind.ENUM.value,
        ApiFieldKind.MODEL.value,
        ApiFieldKind.DTO.value,
    }:
        return _safe_named_or_primitive_type(
            field.type.item_type,
            field.type.item_format,
        )

    if field.type.item_type:
        return _safe_named_or_primitive_type(
            field.type.item_type,
            field.type.item_format,
        )

    return "dynamic"


def _first_schema_ref_type(
    refs: tuple[str, ...],
    schema_by_ref: dict[str, ApiSchema],
) -> str | None:
    for ref in refs:
        ref_type = _schema_ref_type(ref, schema_by_ref)
        if ref_type is not None:
            return ref_type

    return None


def _schema_ref_type(
    ref: str | None,
    schema_by_ref: dict[str, ApiSchema],
) -> str | None:
    if not ref:
        return None

    schema = schema_by_ref.get(ref)
    if schema is None:
        return None

    kind = _kind_value(schema.kind)

    if kind == ApiSchemaKind.PRIMITIVE.value:
        return _primitive_schema_type(schema, schema_by_ref)

    if kind in {
        ApiSchemaKind.ENUM.value,
        ApiSchemaKind.MODEL.value,
        ApiSchemaKind.DTO.value,
    }:
        return str(schema.name.pascal.o)

    return None


def _primitive_schema_type(
    schema: ApiSchema,
    schema_by_ref: dict[str, ApiSchema],
) -> str:
    direct = _dart_primitive_type(schema.primitive_type, schema.primitive_format)
    if direct != "dynamic":
        return direct

    for ref in schema.composition_refs:
        target = schema_by_ref.get(ref)
        if target is None:
            continue

        if _kind_value(target.kind) == ApiSchemaKind.PRIMITIVE.value:
            resolved = _primitive_schema_type(target, schema_by_ref)
            if resolved != "dynamic":
                return resolved

    if schema.alias_of:
        target = schema_by_ref.get(schema.alias_of)
        if target is not None and _kind_value(target.kind) == ApiSchemaKind.PRIMITIVE.value:
            resolved = _primitive_schema_type(target, schema_by_ref)
            if resolved != "dynamic":
                return resolved

    return "dynamic"


def _dart_primitive_type(type_name: str | None, fmt: str | None) -> str:
    normalized = _normalize_type_name(type_name)

    if normalized == "integer":
        return "int"

    if normalized == "number":
        return "double"

    if normalized == "boolean":
        return "bool"

    if normalized == "string" and fmt in _DATE_FORMATS:
        return "DateTime"

    if normalized == "string":
        return "String"

    if normalized == "object":
        return "Map<String, dynamic>"

    return "dynamic"


def _safe_named_or_primitive_type(type_name: str | None, fmt: str | None) -> str:
    normalized = _normalize_type_name(type_name)

    if normalized in _OPENAPI_PRIMITIVES:
        return _dart_primitive_type(normalized, fmt)

    if not type_name:
        return "dynamic"

    return _sanitize_dart_type_name(str(type_name))


def _fallback_type(field: ApiField) -> str:
    if field.type.raw_type:
        return _dart_primitive_type(field.type.raw_type, field.type.format)

    if field.type.type:
        return _safe_named_or_primitive_type(field.type.type, field.type.format)

    return "dynamic"


def _field_schema_refs(field: ApiField) -> tuple[str, ...]:
    return _dedupe_refs((field.schema_ref, *field.schema_refs))


def _field_item_refs(field: ApiField) -> tuple[str, ...]:
    return _dedupe_refs((field.item_ref, *field.item_refs))


def _dedupe_refs(values: tuple[str | None, ...]) -> tuple[str, ...]:
    refs: list[str] = []

    for value in values:
        if value and value not in refs:
            refs.append(value)

    return tuple(refs)


def _schema_is_nullable(schema: ApiSchema) -> bool:
    return bool(getattr(schema, "nullable", False))


def _kind_value(value: object) -> str:
    enum_value = getattr(value, "value", None)
    if isinstance(enum_value, str):
        return enum_value

    if isinstance(value, str):
        return value

    return ""


def _normalize_type_name(value: str | None) -> str:
    return str(value or "").strip()


def _sanitize_dart_type_name(value: str) -> str:
    text = value.strip()

    if not text:
        return "dynamic"

    if "<" in text or ">" in text:
        return text

    if "." in text:
        text = text.rsplit(".", 1)[-1]

    return text[:1].upper() + text[1:]
