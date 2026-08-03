from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from archives.codepotg.src.constants.codegen import X_CODEGEN
from archives.codepotg.src.constants.http import HTTP_METHODS
from archives.codepotg.src.inference.resources import extract_resource_from_x_codegen
from archives.codepotg.src.openapi.document import OpenApiDocument
from archives.codepotg.src.openapi.refs import find_refs
from archives.codepotg.src.openapi.resolver.components import build_component_index


@dataclass(frozen=True)
class ResourceSummary:
    name: str
    path: tuple[str, ...] = field(default_factory=tuple)
    operation_count: int = 0


@dataclass(frozen=True)
class OpenApiInspection:
    title: str
    openapi_version: str
    api_version: str
    path_count: int
    operation_count: int
    schema_count: int
    response_count: int
    request_body_count: int
    parameter_count: int
    ref_count: int
    component_ref_count: int
    missing_component_ref_count: int
    resources: tuple[ResourceSummary, ...]


def inspect_openapi_document(document: OpenApiDocument) -> OpenApiInspection:
    operation_count = 0
    resources: dict[str, ResourceSummary] = {}

    for _, path_item in document.paths.items():
        if not isinstance(path_item, dict):
            continue

        path_resource = _extract_resource(path_item, document)

        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS:
                continue

            if not isinstance(operation, dict):
                continue

            operation_count += 1

            operation_resource = _extract_resource(operation, document) or path_resource
            if operation_resource is None:
                continue

            current = resources.get(operation_resource.name)
            if current is None:
                resources[operation_resource.name] = ResourceSummary(
                    name=operation_resource.name,
                    path=operation_resource.path,
                    operation_count=1,
                )
            else:
                resources[operation_resource.name] = ResourceSummary(
                    name=current.name,
                    path=current.path,
                    operation_count=current.operation_count + 1,
                )

    refs = find_refs(document.raw)
    component_index = build_component_index(document)

    component_refs = tuple(ref for ref in refs if ref.is_component)
    missing_component_refs = tuple(ref for ref in component_refs if not component_index.has(ref))

    return OpenApiInspection(
        title=document.title,
        openapi_version=document.openapi_version,
        api_version=document.api_version,
        path_count=len(document.paths),
        operation_count=operation_count,
        schema_count=len(document.schemas),
        response_count=len(document.responses),
        request_body_count=len(document.request_bodies),
        parameter_count=len(document.parameters),
        ref_count=len(refs),
        component_ref_count=len(component_refs),
        missing_component_ref_count=len(missing_component_refs),
        resources=tuple(sorted(resources.values(), key=lambda item: item.name.lower())),
    )


def _extract_resource(
    node: dict[str, Any],
    document: OpenApiDocument,
) -> ResourceSummary | None:
    x_codegen = node.get(X_CODEGEN)

    if not isinstance(x_codegen, dict):
        return None

    resource = extract_resource_from_x_codegen(x_codegen, document)
    if resource is None:
        return None

    return ResourceSummary(name=resource.name, path=resource.path)
