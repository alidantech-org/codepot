"""Enum schema inference.

This module provides utilities for inferring enum information from
OpenAPI schema objects including enum values and enum type.
"""

from typing import Any

from constants.openapi import ENUM, TYPE, TYPE_NULL


def infer_enum_values(schema: dict[str, Any] | None) -> tuple[str, ...]:
    """Infer enum values from an OpenAPI schema object.

    Args:
        schema: An OpenAPI schema object.

    Returns:
        A tuple of enum value strings, preserving order.
    """
    if not isinstance(schema, dict):
        return ()

    enum_values = schema.get(ENUM)
    if not isinstance(enum_values, list):
        return ()

    # Convert values to strings for consistency, preserving order
    return tuple(str(v) for v in enum_values)


def infer_enum_type(schema: dict[str, Any] | None) -> str | None:
    """Infer enum type from an OpenAPI schema object.

    Args:
        schema: An OpenAPI schema object.

    Returns:
        The enum type string, or None if not found.
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
