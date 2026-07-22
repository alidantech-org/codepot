"""JSON pointer parsing and walking.

This module provides utilities for parsing and resolving JSON pointers
as defined in RFC 6901. JSON pointers are used in OpenAPI specifications
to reference specific parts of a document using a path-like syntax.
"""

from typing import Any

from constants.openapi import JSON_POINTER_PREFIX


def decode_pointer_part(value: str) -> str:
    """Decode a JSON pointer part according to RFC 6901.

    Replaces ~1 with / and ~0 with ~.

    Args:
        value: The encoded pointer part.

    Returns:
        The decoded pointer part.
    """
    return value.replace("~1", "/").replace("~0", "~")


def split_local_ref(ref: str) -> tuple[str, ...]:
    """Split a local JSON reference into its path components.

    Args:
        ref: A local reference string (e.g., "#/components/schemas/User").

    Returns:
        A tuple of path components (e.g., ("components", "schemas", "User")).
    """
    if not ref.startswith(JSON_POINTER_PREFIX):
        return ()

    path = ref[len(JSON_POINTER_PREFIX) :]
    return tuple(decode_pointer_part(part) for part in path.split("/"))


def resolve_pointer(document: dict[str, Any], ref: str) -> Any | None:
    """Resolve a JSON pointer within a document.

    Args:
        document: The OpenAPI document as a dictionary.
        ref: The JSON pointer reference to resolve.

    Returns:
        The resolved value, or None if the pointer cannot be resolved.
    """
    parts = split_local_ref(ref)

    if not parts:
        return None

    current: Any = document

    for part in parts:
        if not isinstance(current, dict):
            return None

        if part not in current:
            return None

        current = current[part]

    return current
