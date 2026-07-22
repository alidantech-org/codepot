from __future__ import annotations

from typing import Any

from constants.codegen import X_CODEGEN, KIND, KIND_PRIMITIVE, KIND_ENUM, KIND_MODEL, KIND_DTO
from constants.openapi import (
    REF,
    TYPE,
    PROPERTIES,
    ALL_OF,
    ENUM,
    TYPE_OBJECT,
    TYPE_STRING,
    TYPE_INTEGER,
    TYPE_NUMBER,
    TYPE_BOOLEAN,
    TYPE_NULL,
)
from inference.models import InferredSchemaKind
from openapi.document import OpenApiDocument


def classify_schema(
    name: str,
    schema: dict[str, Any],
    document: OpenApiDocument | None = None,
    seen_refs: set[str] | None = None,
) -> InferredSchemaKind:
    x_codegen = schema.get(X_CODEGEN)

    if isinstance(x_codegen, dict):
        explicit_kind = x_codegen.get(KIND)
        if isinstance(explicit_kind, str):
            mapped = _map_codegen_kind(explicit_kind)
            if mapped is not None:
                return mapped

    if REF in schema and document is not None:
        from inference.ref_metadata import infer_kind_from_ref_alias

        inferred = infer_kind_from_ref_alias(schema, document, seen_refs)
        if inferred is not None:
            return inferred

    if _is_enum_schema(schema):
        return InferredSchemaKind.ENUM

    if _is_object_schema(schema):
        return InferredSchemaKind.MODEL

    if _is_primitive_schema(schema):
        return InferredSchemaKind.PRIMITIVE

    return InferredSchemaKind.UNKNOWN


def _map_codegen_kind(value: str) -> InferredSchemaKind | None:
    normalized = value.strip().lower().replace("-", "_")

    mapping = {
        KIND_ENUM: InferredSchemaKind.ENUM,
        KIND_MODEL: InferredSchemaKind.MODEL,
        KIND_DTO: InferredSchemaKind.DTO,
        KIND_PRIMITIVE: InferredSchemaKind.PRIMITIVE,
    }

    return mapping.get(normalized)


def _is_enum_schema(schema: dict[str, Any]) -> bool:
    return isinstance(schema.get(ENUM), list)


def _is_object_schema(schema: dict[str, Any]) -> bool:
    if schema.get(TYPE) == TYPE_OBJECT:
        return True

    if isinstance(schema.get(PROPERTIES), dict):
        return True

    if isinstance(schema.get(ALL_OF), list):
        return True

    return False


def _is_primitive_schema(schema: dict[str, Any]) -> bool:
    schema_type = schema.get(TYPE)

    if isinstance(schema_type, str):
        return schema_type in {TYPE_STRING, TYPE_INTEGER, TYPE_NUMBER, TYPE_BOOLEAN, TYPE_NULL}

    if isinstance(schema_type, list):
        return any(item in {TYPE_STRING, TYPE_INTEGER, TYPE_NUMBER, TYPE_BOOLEAN, TYPE_NULL} for item in schema_type)

    return False
