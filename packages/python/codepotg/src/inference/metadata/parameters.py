"""Read x-codegen parameter target metadata.

This module provides utilities for reading optional x-codegen parameter
target metadata from operation nodes. It does not resolve references,
classify schemas, or make code-generation decisions. It only extracts
metadata values as written.
"""

from typing import Any

from constants.codegen import TARGET, X_CODEGEN
from constants.openapi import PARAMETERS, REF

def get_parameter_target_refs(node: dict[str, Any] | None) -> tuple[str, ...]:
    """Return parameter target refs from x-codegen metadata.

    Args:
        node: An operation node that may contain x-codegen metadata.

    Returns:
        A tuple of schema reference strings from x-codegen.parameters.target
        or x-codegen.parameters.targets. Returns empty tuple if no metadata exists.
    """
    if not isinstance(node, dict):
        return ()

    x_codegen = node.get(X_CODEGEN)
    if not isinstance(x_codegen, dict):
        return ()

    parameters = x_codegen.get(PARAMETERS)
    if not isinstance(parameters, dict):
        return ()

    refs: list[str] = []

    # Check for single target
    target = parameters.get(TARGET)
    if isinstance(target, dict):
        ref = target.get(REF)
        if isinstance(ref, str):
            refs.append(ref)

    return tuple(refs)


def get_parameter_target_source(node: dict[str, Any] | None) -> str | None:
    """Return the source label for parameter target metadata.

    Args:
        node: An operation node that may contain x-codegen metadata.

    Returns:
        The source label (e.g., "x-codegen.parameters.target") if metadata exists,
        or None if no metadata exists.
    """
    if not isinstance(node, dict):
        return None

    x_codegen = node.get(X_CODEGEN)
    if not isinstance(x_codegen, dict):
        return None

    parameters = x_codegen.get(PARAMETERS)
    if not isinstance(parameters, dict):
        return None

    if TARGET in parameters:
        return f"{X_CODEGEN}.{PARAMETERS}.{TARGET}"

    return None
