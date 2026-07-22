"""Connect codegen parameter targets to inferred parameters.

This module provides utilities for connecting x-codegen parameter target
metadata to actual inferred parameters from OpenAPI operations.
"""

from typing import Any
from inference.metadata.parameters import get_parameter_target_refs, get_parameter_target_source
from inference.models import InferredParameter, InferredParameterTarget


def infer_parameter_targets(
    operation_node: dict[str, Any] | None,
    parameters: tuple[InferredParameter, ...],
) -> tuple[InferredParameterTarget, ...]:
    """Infer parameter targets from operation metadata and parameters.

    Args:
        operation_node: The operation node that may contain x-codegen metadata.
        parameters: The inferred parameters from the operation.

    Returns:
        A tuple of InferredParameterTarget objects connecting target refs
        to actual parameter locations and names.
    """
    target_refs = get_parameter_target_refs(operation_node)
    source = get_parameter_target_source(operation_node)

    if not target_refs:
        return ()

    # Extract unique locations and parameter names from actual parameters
    locations = tuple(sorted(set(param.location for param in parameters)))
    parameter_names = tuple(sorted(set(param.name for param in parameters)))

    # Create a target for each ref
    targets: list[InferredParameterTarget] = []

    for ref in target_refs:
        targets.append(
            InferredParameterTarget(
                ref=ref,
                source=source,
                locations=locations,
                parameter_names=parameter_names,
            )
        )

    return tuple(targets)
