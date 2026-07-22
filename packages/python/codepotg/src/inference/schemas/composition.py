"""Schema composition inference.

This module provides utilities for inferring composition information from
OpenAPI schema objects including allOf, anyOf, and oneOf.
"""

from typing import Any

from constants.openapi import ALL_OF, ANY_OF, ONE_OF, COMPOSITION_ALL_OF, COMPOSITION_ANY_OF, COMPOSITION_ONE_OF
from openapi.refs import get_ref

from inference.models.schemas import InferredSchemaComposition


def split_nullable_union(schema: dict[str, Any] | None) -> tuple[dict[str, Any], bool]:
    """Return non-null schema branch and whether null was present.

    Args:
        schema: An OpenAPI schema object.

    Returns:
        A tuple of (non_null_schema, nullable) where nullable is True if
        null was present in the union.
    """
    if not isinstance(schema, dict):
        return schema or {}, False

    schema_type = schema.get("type")

    # Handle type: [string, null]
    if isinstance(schema_type, list) and "null" in schema_type:
        non_null_types = [item for item in schema_type if item != "null"]

        if len(non_null_types) == 1:
            copied = dict(schema)
            copied["type"] = non_null_types[0]
            return copied, True

    # Handle anyOf/oneOf with type: null
    variants = schema.get(ANY_OF) or schema.get(ONE_OF)

    if isinstance(variants, list):
        nullable = False
        non_null_variants = []

        for variant in variants:
            if isinstance(variant, dict) and variant.get("type") == "null":
                nullable = True
            else:
                non_null_variants.append(variant)

        if nullable and len(non_null_variants) == 1:
            return non_null_variants[0], True

    return schema, False


def infer_composition(schema: dict[str, Any] | None) -> InferredSchemaComposition | None:
    """Infer composition from an OpenAPI schema object.

    Args:
        schema: An OpenAPI schema object.

    Returns:
        An InferredSchemaComposition object if composition exists, None otherwise.
    """
    if not isinstance(schema, dict):
        return None

    # Check for allOf
    all_of = schema.get(ALL_OF)
    if isinstance(all_of, list) and all_of:
        refs = _get_composition_refs(all_of)
        inline_count = _count_inline_objects(all_of)
        return InferredSchemaComposition(
            kind=COMPOSITION_ALL_OF,
            refs=refs,
            inline_field_count=inline_count,
        )

    # Check for anyOf
    any_of = schema.get(ANY_OF)
    if isinstance(any_of, list) and any_of:
        refs = _get_composition_refs(any_of)
        inline_count = _count_inline_objects(any_of)
        return InferredSchemaComposition(
            kind=COMPOSITION_ANY_OF,
            refs=refs,
            inline_field_count=inline_count,
        )

    # Check for oneOf
    one_of = schema.get(ONE_OF)
    if isinstance(one_of, list) and one_of:
        refs = _get_composition_refs(one_of)
        inline_count = _count_inline_objects(one_of)
        return InferredSchemaComposition(
            kind=COMPOSITION_ONE_OF,
            refs=refs,
            inline_field_count=inline_count,
        )

    return None


def get_composition_refs(schema: dict[str, Any] | None) -> tuple[str, ...]:
    """Get all composition refs from an OpenAPI schema object.

    Args:
        schema: An OpenAPI schema object.

    Returns:
        A tuple of schema reference strings from allOf/anyOf/oneOf.
    """
    if not isinstance(schema, dict):
        return ()

    refs: list[str] = []

    for key in (ALL_OF, ANY_OF, ONE_OF):
        items = schema.get(key)
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    ref = get_ref(item)
                    if ref:
                        refs.append(ref.raw)

    return tuple(refs)


def get_inherited_refs(schema: dict[str, Any] | None) -> tuple[str, ...]:
    """Get inherited refs from allOf (used for inheritance).

    Args:
        schema: An OpenAPI schema object.

    Returns:
        A tuple of schema reference strings from allOf only.
    """
    if not isinstance(schema, dict):
        return ()

    refs: list[str] = []

    all_of = schema.get(ALL_OF)
    if isinstance(all_of, list):
        for item in all_of:
            if isinstance(item, dict):
                ref = get_ref(item)
                if ref:
                    refs.append(ref.raw)

    return tuple(refs)


def _get_composition_refs(items: list[dict[str, Any]]) -> tuple[str, ...]:
    """Get refs from a composition items list.

    Args:
        items: A list of composition items (allOf/anyOf/oneOf).

    Returns:
        A tuple of schema reference strings.
    """
    refs: list[str] = []

    for item in items:
        if isinstance(item, dict):
            ref = get_ref(item)
            if ref:
                refs.append(ref.raw)

    return tuple(refs)


def _count_inline_objects(items: list[dict[str, Any]]) -> int:
    """Count inline objects in a composition items list.

    Args:
        items: A list of composition items (allOf/anyOf/oneOf).

    Returns:
        The count of inline objects (non-ref items).
    """
    count = 0

    for item in items:
        if isinstance(item, dict):
            if get_ref(item) is None:
                count += 1

    return count
