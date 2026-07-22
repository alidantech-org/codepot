"""Standard parameter resolution and schema refs.

This module provides utilities for resolving parameter references
and extracting information from parameter objects.
"""

from typing import Any

from constants.openapi import PARAMETERS, REF_PARAMETERS, PARAM_IN, PARAM_NAME, REF, REQUIRED, SCHEMA
from openapi.document import OpenApiDocument
from openapi.refs import get_ref


def resolve_parameter(document: OpenApiDocument, parameter_node: dict[str, Any]) -> dict[str, Any] | None:
    """Resolve a parameter node to its definition.

    If the parameter node contains a $ref, the reference is resolved.
    Otherwise, the node itself is returned.

    Args:
        document: The OpenAPI document.
        parameter_node: The parameter node to resolve.

    Returns:
        The resolved parameter definition, or None if resolution fails.
    """
    ref = parameter_node.get(REF)

    if ref is None:
        return parameter_node

    if not isinstance(ref, str):
        return None

    if not ref.startswith(REF_PARAMETERS):
        return None

    name = ref.replace(REF_PARAMETERS, "")
    parameters = document.components.get(PARAMETERS)

    if not isinstance(parameters, dict):
        return None

    return parameters.get(name)


def get_parameter_schema_refs(parameter_node: dict[str, Any]) -> tuple[str, ...]:
    """Extract schema refs from a parameter node.

    Args:
        parameter_node: The parameter node to extract schema refs from.

    Returns:
        A tuple of schema reference strings.
    """
    schema = parameter_node.get(SCHEMA)
    ref = get_ref(schema)

    if ref is not None:
        return (ref.raw,)

    return ()


def get_parameter_location(parameter_node: dict[str, Any]) -> str | None:
    """Get the location (in) of a parameter.

    Args:
        parameter_node: The parameter node to extract the location from.

    Returns:
        The parameter location (e.g., "query", "path", "header"), or None.
    """
    location = parameter_node.get(PARAM_IN)

    if isinstance(location, str):
        return location

    return None


def get_parameter_name(parameter_node: dict[str, Any]) -> str | None:
    """Get the name of a parameter.

    Args:
        parameter_node: The parameter node to extract the name from.

    Returns:
        The parameter name, or None.
    """
    name = parameter_node.get(PARAM_NAME)

    if isinstance(name, str):
        return name

    return None


def is_parameter_required(parameter_node: dict[str, Any]) -> bool:
    """Check if a parameter is required.

    Args:
        parameter_node: The parameter node to check.

    Returns:
        True if the parameter is required, False otherwise.
    """
    required = parameter_node.get(REQUIRED)

    return bool(required)
