from __future__ import annotations

from copy import deepcopy

from constants.codegen import ATTR_RESOURCE, X_CODEGEN
from inference.graph import collect_dependencies
from inference.models import InferenceGraph, InferredResource
from inference.operations.engine import infer_operations
from inference.schemas import infer_schemas
from openapi.document import OpenApiDocument


def _clean_optional_text(value: object) -> str:
    if not isinstance(value, str):
        return ""

    cleaned = value.strip()

    if not cleaned or cleaned == "-":
        return ""

    return cleaned


class InferenceEngine:
    def infer(self, document: OpenApiDocument) -> InferenceGraph:
        schemas = infer_schemas(document)
        operations = infer_operations(document)
        resources = _collect_resources(schemas, operations)
        dependencies = collect_dependencies(schemas, operations)

        # Propagate resource information from operations to schemas
        schemas = _propagate_resources_to_schemas(schemas, operations, resources)

        x_codegen = document.raw.get(X_CODEGEN)

        return InferenceGraph(
            title=document.title,
            openapi_version=document.openapi_version,
            api_version=document.api_version,
            description=_clean_optional_text(document.description),
            servers=document.servers,
            resources=resources,
            schemas=schemas,
            operations=operations,
            dependencies=dependencies,
            x_codegen=x_codegen if isinstance(x_codegen, dict) else {},
            raw=deepcopy(document.raw),
        )


def _collect_resources(
    schemas: tuple,
    operations: tuple,
) -> tuple[InferredResource, ...]:
    resources: dict[str, InferredResource] = {}

    for item in (*schemas, *operations):
        resource = getattr(item, ATTR_RESOURCE, None)

        if resource is None:
            continue

        existing = resources.get(resource.name)
        if existing is None:
            resources[resource.name] = resource
            continue

        if not existing.path and resource.path:
            resources[resource.name] = resource

    return tuple(sorted(resources.values(), key=lambda item: item.name.lower()))


def _propagate_resources_to_schemas(
    schemas: tuple,
    operations: tuple,
    resources: tuple[InferredResource, ...],
) -> tuple:
    """Assign resources to schemas based on which operations use them."""
    # Build a map of schema ref to resource from operations
    schema_to_resource: dict[str, InferredResource] = {}

    for operation in operations:
        op_resource = operation.resource
        if op_resource is None:
            continue

        # Collect all schema refs from the operation
        refs = set()

        # From parameters
        for param in operation.parameters:
            if param.schema_ref:
                refs.add(param.schema_ref)
            refs.update(param.schema_refs)

        # From request body
        if operation.request_body:
            refs.update(operation.request_body.schema_refs)

        # From responses
        for response in operation.responses:
            refs.update(response.schema_refs)

        # Assign the operation's resource to all referenced schemas
        for ref in refs:
            if ref not in schema_to_resource:
                schema_to_resource[ref] = op_resource

    # Update schemas that don't have a resource but are used by operations
    schema_list = list(schemas)
    for i, schema in enumerate(schema_list):
        if schema.resource is None:
            resource = schema_to_resource.get(schema.ref)
            if resource:
                # Create a new schema with the resource assigned
                from dataclasses import replace

                schema_list[i] = replace(schema, resource=resource)

    return tuple(schema_list)
