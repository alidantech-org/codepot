"""Dart resource template builders."""

from __future__ import annotations

from contracts.api import ApiResource
from contracts.template import (
    TemplateDependency,
    TemplateDocs,
    TemplateGroup,
    TemplateItemEmit,
    TemplateItemKey,
    TemplateOperation,
    TemplateResource,
    TemplateResourceLang,
    TemplateResourceMeta,
    TemplateSchemaGroups,
)
from languages.dart.operations import operations_for_resource
from languages.dart.paths import resource_path_for_resource


def resource_paths(resources: tuple[ApiResource, ...]) -> dict[str, tuple[str, ...]]:
    """Return resource paths keyed by resource id."""
    return {resource.id: resource_path_for_resource(resource) for resource in resources}


def _operation_dependencies(operations: tuple[TemplateOperation, ...]) -> tuple[TemplateDependency, ...]:
    """Aggregate unique dependencies from operations for a resource."""
    seen: set[tuple[str, str]] = set()
    dependencies: list[TemplateDependency] = []

    for operation in operations:
        emit = operation.emit
        if emit is None:
            continue

        for dependency in emit.dependencies:
            key = (dependency.ref, str(dependency.purpose))
            if key in seen:
                continue

            seen.add(key)
            dependencies.append(dependency)

    return tuple(dependencies)


def template_resources(
    resources: tuple[ApiResource, ...],
    *,
    schemas: TemplateSchemaGroups,
    operations: tuple[TemplateOperation, ...] = (),
) -> tuple[TemplateResource, ...]:
    """Build Dart resources with grouped children."""
    return tuple(_resource(resource, schemas=schemas, operations=operations) for resource in resources)


def feature_resources(resources: tuple[TemplateResource, ...]) -> tuple[TemplateResource, ...]:
    """Return Dart resources that should emit feature clients."""
    return tuple(resource for resource in resources if resource.operations)


def _resource(
    resource: ApiResource,
    *,
    schemas: TemplateSchemaGroups,
    operations: tuple[TemplateOperation, ...],
) -> TemplateResource:
    resource_path = resource_path_for_resource(resource)

    models = _items_for_resource(schemas.emit_models, resource_path)
    dtos = _items_for_resource(schemas.emit_dtos, resource_path)
    enums = _items_for_resource(schemas.emit_enums, resource_path)
    resource_operations = operations_for_resource(operations, resource_path)

    return TemplateResource(
        api=resource,
        name=resource.name,
        path=resource.path,
        path_name=resource.path_name,
        operations=resource_operations,
        models=models,
        dtos=dtos,
        enums=enums,
        schemas=(*models, *dtos, *enums),
        lang=TemplateResourceLang(
            kind="dart_resource",
            display_name=resource.name.pascal.o,
        ),
        emit=TemplateItemEmit(
            group=TemplateGroup.RESOURCES,
            item_key=TemplateItemKey.RESOURCE,
            key=resource.id,
            resource_path=resource_path,
            folder_path=resource_path,
            file_name="index",
            path_parts=(TemplateGroup.RESOURCES.value, resource.name.path.o),
            dependencies=_operation_dependencies(resource_operations),
        ),
        docs=TemplateDocs(),
        meta=TemplateResourceMeta(
            operations_count=resource.operations_count,
        ),
    )


def _items_for_resource(items: tuple, resource_path: tuple[str, ...]) -> tuple:
    return tuple(item for item in items if item.emit is not None and item.emit.resource_path == resource_path)
