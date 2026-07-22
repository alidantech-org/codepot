"""Read x-codegen target metadata.

This module provides utilities for reading the generic x-codegen.target
metadata from operation nodes. It does not resolve references, infer roles,
or make code-generation decisions. It only extracts metadata values as written.
"""

from typing import Any

from constants.codegen import TARGET, X_CODEGEN
from constants.openapi import REF


def get_codegen_target_ref(node: dict[str, Any] | None) -> str | None:
    """Return the target ref from x-codegen.target.$ref.

    Args:
        node: An operation node that may contain x-codegen metadata.

    Returns:
        The schema reference string from x-codegen.target.$ref,
        or None if no metadata exists.
    """
    if not isinstance(node, dict):
        return None

    x_codegen = node.get(X_CODEGEN)
    if not isinstance(x_codegen, dict):
        return None

    target = x_codegen.get(TARGET)
    if not isinstance(target, dict):
        return None

    ref = target.get(REF)
    if isinstance(ref, str):
        return ref

    return None


def get_codegen_target_source(node: dict[str, Any] | None) -> str | None:
    """Return the source label for target metadata.

    Args:
        node: An operation node that may contain x-codegen metadata.

    Returns:
        The source label (e.g., "x-codegen.target") if metadata exists,
        or None if no metadata exists.
    """
    if not isinstance(node, dict):
        return None

    x_codegen = node.get(X_CODEGEN)
    if not isinstance(x_codegen, dict):
        return None

    if TARGET in x_codegen:
        return f"{X_CODEGEN}.{TARGET}"

    return None
