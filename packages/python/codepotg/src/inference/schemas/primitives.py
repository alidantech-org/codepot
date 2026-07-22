"""Primitive schema inference.

This module provides utilities for inferring primitive type information
from OpenAPI schema objects including type and format.
"""

from typing import Any

from constants.openapi import FORMAT, TYPE, TYPE_NULL


def infer_primitive_type(schema: dict[str, Any] | None) -> str | None:
    """Infer primitive type from an OpenAPI schema object.

    Args:
        schema: An OpenAPI schema object.

    Returns:
        The primitive type string, or None if not found.
    """
    if not isinstance(schema, dict):
        return None

    raw_type = schema.get(TYPE)
    if isinstance(raw_type, str):
        return raw_type

    if isinstance(raw_type, list):
        # Get the non-null type from type arrays
        non_null_types = [t for t in raw_type if t != TYPE_NULL]
        return non_null_types[0] if non_null_types else None

    return None


def infer_primitive_format(schema: dict[str, Any] | None) -> str | None:
    """Infer primitive format from an OpenAPI schema object.

    Args:
        schema: An OpenAPI schema object.

    Returns:
        The format string, or None if not found.
    """
    if not isinstance(schema, dict):
        return None

    format_value = schema.get(FORMAT)
    if isinstance(format_value, str):
        return format_value

    return None
