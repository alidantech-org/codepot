"""Dart output path helpers."""

from __future__ import annotations

from contracts.api import ApiResource, ApiSchema
from languages.dart.names import name_text
from languages.debug.context.path_values import safe_file_name, safe_path_parts

SHARED_PATH = ("shared",)


def resource_path_for_resource(resource: ApiResource) -> tuple[str, ...]:
    """Return the Dart resource folder path for a resource."""
    base_path = safe_path_parts(resource.path, fallback="")
    name_path = safe_path_parts(name_text(resource.name.path.o), fallback=resource.id)

    if base_path == ("",):
        return name_path or SHARED_PATH

    if base_path[-len(name_path) :] == name_path:
        return base_path

    return (*base_path, *name_path)


def resource_path_for_schema(
    schema: ApiSchema,
    resource_paths: dict[str, tuple[str, ...]],
) -> tuple[str, ...]:
    """Return the Dart resource folder path for a schema."""
    if schema.resource and schema.resource in resource_paths:
        return resource_paths[schema.resource]

    return safe_path_parts(schema.resource, fallback="shared")


def safe_schema_file_name(schema: ApiSchema) -> str:
    """Return a safe Dart schema folder/file name."""
    return safe_file_name(name_text(schema.name.path.o), fallback=schema.id)
