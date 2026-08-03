from __future__ import annotations

from typing import Any

from archives.codepotg.src.constants.codegen import X_CODEGEN
from archives.codepotg.src.constants.http import HTTP_METHODS
from archives.codepotg.src.constants.openapi import OPERATION_ID, REQUEST_BODY, RESPONSES
from archives.codepotg.src.inference.metadata.parameters import get_parameter_target_refs, get_parameter_target_source
from archives.codepotg.src.inference.metadata.targets import get_codegen_target_ref, get_codegen_target_source
from archives.codepotg.src.inference.metadata.ui import get_operation_ui_metadata
from archives.codepotg.src.inference.models import InferredOperation, InferredOperationTarget
from archives.codepotg.src.inference.operations.parameters import infer_parameters
from archives.codepotg.src.inference.operations.request_bodies import infer_request_body
from archives.codepotg.src.inference.operations.resources import infer_resource
from archives.codepotg.src.inference.operations.responses import infer_responses
from archives.codepotg.src.inference.resources import extract_resource_from_x_codegen
from archives.codepotg.src.openapi.document import OpenApiDocument
from archives.codepotg.src.openapi.resolver.parameters import resolve_parameter


def infer_operations(document: OpenApiDocument) -> tuple[InferredOperation, ...]:
    operations: list[InferredOperation] = []

    for path, path_item in document.paths.items():
        if not isinstance(path_item, dict):
            continue

        path_resource = extract_resource_from_x_codegen(path_item.get(X_CODEGEN, {}), document)

        for method, operation in path_item.items():
            lower = method.lower()

            if lower not in HTTP_METHODS:
                continue

            if not isinstance(operation, dict):
                continue

            resource = infer_resource(operation, path_item, path_resource, document)
            merged_params = _merged_parameters(path_item, operation, document)
            parameters = infer_parameters(merged_params, document)
            request_body = infer_request_body(operation.get(REQUEST_BODY), document)
            responses = infer_responses(operation.get(RESPONSES), document)
            target = infer_operation_target(operation, parameters, request_body, responses)
            ui = get_operation_ui_metadata(operation)

            operations.append(
                InferredOperation(
                    operation_id=_operation_id(lower, str(path), operation),
                    method=upper(lower),
                    path=str(path),
                    resource=resource,
                    parameters=parameters,
                    request_body=request_body,
                    responses=responses,
                    target=target,
                    ui=ui,
                    raw=operation,
                )
            )

    return tuple(operations)


def infer_operation_target(
    operation: dict,
    parameters: tuple,
    request_body,
    responses: tuple,
) -> InferredOperationTarget | None:
    """Infer generic operation target from x-codegen.target metadata.

    Args:
        operation: The operation node.
        parameters: Inferred parameters.
        request_body: Inferred request body.
        responses: Inferred responses.

    Returns:
        An InferredOperationTarget if target metadata exists, None otherwise.
    """
    target_ref = get_codegen_target_ref(operation)
    source = get_codegen_target_source(operation) or "x-codegen.target"

    if not target_ref:
        parameter_target_refs = get_parameter_target_refs(operation)
        target_ref = parameter_target_refs[0] if parameter_target_refs else None
        source = get_parameter_target_source(operation) or "x-codegen.parameters.target"

    if not target_ref:
        return None

    parameter_target = source == "x-codegen.parameters.target"

    # Infer roles from operation context
    inferred_roles: list[str] = []
    locations: list[str] = []

    if parameters:
        param_locations = set(param.location for param in parameters)
        locations.extend(param_locations)

        if "query" in param_locations:
            inferred_roles.append("query")
        if "path" in param_locations:
            inferred_roles.append("params")

    if request_body and not parameter_target:
        inferred_roles.append("body")

    if responses and not parameter_target:
        success_responses = [r for r in responses if r.is_success]
        if success_responses:
            inferred_roles.append("response")

    return InferredOperationTarget(
        ref=target_ref,
        source=source,
        exclude=(),
        inferred_roles=tuple(sorted(set(inferred_roles))),
        locations=tuple(sorted(set(locations))),
        reason="inferred from operation context",
    )


def _merged_parameters(
    path_item: dict[str, Any],
    operation: dict[str, Any],
    document: OpenApiDocument,
) -> list[dict[str, Any]]:
    """Merge path-level and operation-level parameters.

    Operation-level parameters override path-level parameters by name + in.

    Args:
        path_item: The OpenAPI path item object.
        operation: The OpenAPI operation object.

    Returns:
        Merged list of parameter objects.
    """
    merged: dict[tuple[str, str], dict[str, Any]] = {}

    for raw_parameter in path_item.get("parameters", []):
        parameter = _mergeable_parameter(raw_parameter, document)
        if parameter is None:
            continue

        key = (
            str(parameter.get("name", "")),
            str(parameter.get("in", "")),
        )
        merged[key] = parameter

    for raw_parameter in operation.get("parameters", []):
        parameter = _mergeable_parameter(raw_parameter, document)
        if parameter is None:
            continue

        key = (
            str(parameter.get("name", "")),
            str(parameter.get("in", "")),
        )
        merged[key] = parameter

    return list(merged.values())


def _mergeable_parameter(
    parameter: Any,
    document: OpenApiDocument,
) -> dict[str, Any] | None:
    if not isinstance(parameter, dict):
        return None

    resolved = resolve_parameter(document, parameter)
    if not isinstance(resolved, dict):
        return None

    if "$ref" not in parameter:
        return resolved

    merged = dict(resolved)
    merged["$ref"] = parameter["$ref"]
    return merged


def upper(method: str) -> str:
    return method.upper()


def _operation_id(method: str, path: str, operation: dict) -> str:
    explicit = operation.get(OPERATION_ID)
    if isinstance(explicit, str) and explicit:
        return explicit

    safe_path = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
    return f"{method}_{safe_path}"
