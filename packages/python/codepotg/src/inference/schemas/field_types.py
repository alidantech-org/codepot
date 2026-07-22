"""Field type resolution.

This module provides utilities for resolving field type information
from schema nodes to make fields self-contained for emitters.
"""

from dataclasses import dataclass
from typing import Any

from constants.openapi import REF_SCHEMAS, ITEMS, TYPE, TYPE_ARRAY, TYPE_NULL
from inference.classifiers import classify_schema
from inference.schemas.primitives import infer_primitive_format
from inference.schemas.resolution import resolve_schema_alias
from openapi.document import OpenApiDocument
from openapi.refs import get_ref


@dataclass(frozen=True)
class ResolvedFieldType:
    """Resolved field type information."""

    resolved_kind: str | None
    resolved_type: str | None
    resolved_format: str | None
    resolved_item_kind: str | None
    resolved_item_type: str | None
    resolved_item_format: str | None


def infer_field_type(field_schema: dict[str, Any], document: OpenApiDocument) -> ResolvedFieldType:
    """Infer resolved field type information from a schema node.

    Args:
        field_schema: A schema object for a field property.
        document: The OpenAPI document for alias resolution.

    Returns:
        A ResolvedFieldType object with resolved type facts.
    """
    # Resolve effective schema for type details
    effective_schema = resolve_schema_alias(document, field_schema) or field_schema

    # Determine if this is an array
    is_array = effective_schema.get(TYPE) == TYPE_ARRAY

    if is_array:
        return _infer_array_type(effective_schema, document)
    else:
        return _infer_scalar_type(effective_schema, document)


def _infer_scalar_type(schema: dict[str, Any], document: OpenApiDocument) -> ResolvedFieldType:
    """Infer type information for scalar (non-array) fields."""
    # Check if this is a ref to a schema
    ref_info = get_ref(schema)
    if ref_info and ref_info.is_component:
        # Resolve the target schema to get its kind and type
        target_schema = _resolve_ref_schema(document, ref_info.raw)
        if target_schema:
            kind = classify_schema("", target_schema, document=document)
            return ResolvedFieldType(
                resolved_kind=kind.value,
                resolved_type=_get_type_from_schema(target_schema),
                resolved_format=infer_primitive_format(target_schema),
                resolved_item_kind=None,
                resolved_item_type=None,
                resolved_item_format=None,
            )

    # Direct primitive or inline schema
    kind = classify_schema("", schema, document=document)
    return ResolvedFieldType(
        resolved_kind=kind.value,
        resolved_type=_get_type_from_schema(schema),
        resolved_format=infer_primitive_format(schema),
        resolved_item_kind=None,
        resolved_item_type=None,
        resolved_item_format=None,
    )


def _infer_array_type(schema: dict[str, Any], document: OpenApiDocument) -> ResolvedFieldType:
    """Infer type information for array fields."""
    items_schema = schema.get(ITEMS)

    if not isinstance(items_schema, dict):
        return ResolvedFieldType(
            resolved_kind=TYPE_ARRAY,
            resolved_type=TYPE_ARRAY,
            resolved_format=None,
            resolved_item_kind=None,
            resolved_item_type=None,
            resolved_item_format=None,
        )

    # Resolve effective items schema
    effective_items = resolve_schema_alias(document, items_schema) or items_schema

    # Check if items is a ref
    items_ref_info = get_ref(items_schema)
    if items_ref_info and items_ref_info.is_component:
        target_schema = _resolve_ref_schema(document, items_ref_info.raw)
        if target_schema:
            item_kind = classify_schema("", target_schema, document=document)
            return ResolvedFieldType(
                resolved_kind=TYPE_ARRAY,
                resolved_type=TYPE_ARRAY,
                resolved_format=None,
                resolved_item_kind=item_kind.value,
                resolved_item_type=_get_type_from_schema(target_schema),
                resolved_item_format=infer_primitive_format(target_schema),
            )

    # Direct items schema
    item_kind = classify_schema("", effective_items, document=document)
    return ResolvedFieldType(
        resolved_kind=TYPE_ARRAY,
        resolved_type=TYPE_ARRAY,
        resolved_format=None,
        resolved_item_kind=item_kind.value,
        resolved_item_type=_get_type_from_schema(effective_items),
        resolved_item_format=infer_primitive_format(effective_items),
    )


def _resolve_ref_schema(document: OpenApiDocument, ref: str) -> dict[str, Any] | None:
    """Resolve a component schema ref to its schema object."""
    if ref.startswith(REF_SCHEMAS):
        schema_name = ref[len(REF_SCHEMAS) :]
        return document.schemas.get(schema_name)
    return None


def _get_type_from_schema(schema: dict[str, Any]) -> str | None:
    """Extract type string from a schema, handling type arrays."""
    raw_type = schema.get(TYPE)
    if isinstance(raw_type, str):
        return raw_type
    if isinstance(raw_type, list):
        # Get the non-null type from type arrays
        non_null_types = [t for t in raw_type if t != TYPE_NULL]
        return non_null_types[0] if non_null_types else None
    return None
