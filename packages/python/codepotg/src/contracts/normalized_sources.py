from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from types import MappingProxyType
from typing import Any

from contracts.normalized import SourceObject, source_object
from contracts.normalized_api import NormalizedApiView

_COMPONENT_COLLECTIONS = (
    "schemas",
    "parameters",
    "requestBodies",
    "responses",
    "headers",
    "examples",
    "links",
    "callbacks",
    "securitySchemes",
    "pathItems",
)
_CODEGEN_COLLECTIONS = (
    "resources",
    "access",
    "entities",
    "baseEntities",
    "frontends",
)


def extend_normalized_source_registry(
    view: NormalizedApiView,
    raw: Mapping[str, Any] | None,
) -> NormalizedApiView:
    """Add immutable source entries for all supported OpenAPI/codegen objects."""

    document = raw or {}
    objects = dict(view.raw_objects)

    info = _mapping(document.get("info"))
    if info:
        objects.setdefault(
            "info",
            source_object(
                info,
                source_path="info",
                known_keys={
                    "title",
                    "summary",
                    "description",
                    "termsOfService",
                    "contact",
                    "license",
                    "version",
                },
            ),
        )

    for index, server in enumerate(_sequence(document.get("servers"))):
        value = _mapping(server)
        objects.setdefault(
            f"server:{index}",
            source_object(
                value,
                source_path=f"servers.{index}",
                known_keys={"url", "description", "variables"},
            ),
        )
        for name, variable in _mapping(value.get("variables")).items():
            objects[f"server:{index}:variable:{name}"] = source_object(
                _mapping(variable),
                source_path=f"servers.{index}.variables.{name}",
                known_keys={"enum", "default", "description"},
            )

    paths = _mapping(document.get("paths"))
    for path, path_item in paths.items():
        value = _mapping(path_item)
        objects.setdefault(
            f"path:{path}",
            source_object(
                value,
                source_path=f"paths.{path}",
                known_keys={
                    "$ref",
                    "summary",
                    "description",
                    "servers",
                    "parameters",
                    "get",
                    "put",
                    "post",
                    "delete",
                    "patch",
                    "options",
                    "head",
                    "trace",
                },
            ),
        )
        _add_parameter_sources(
            objects,
            value.get("parameters"),
            prefix=f"path:{path}:parameter",
            source_path=f"paths.{path}.parameters",
        )
        for method in ("get", "put", "post", "delete", "patch", "options", "head", "trace"):
            operation = _mapping(value.get(method))
            if not operation:
                continue
            operation_key = _operation_key(path, method, operation)
            objects.setdefault(
                operation_key,
                source_object(
                    operation,
                    source_path=f"paths.{path}.{method}",
                    known_keys={
                        "tags",
                        "summary",
                        "description",
                        "externalDocs",
                        "operationId",
                        "parameters",
                        "requestBody",
                        "responses",
                        "callbacks",
                        "deprecated",
                        "security",
                        "servers",
                        "x-codegen",
                    },
                ),
            )
            _add_parameter_sources(
                objects,
                operation.get("parameters"),
                prefix=f"{operation_key}:parameter",
                source_path=f"paths.{path}.{method}.parameters",
            )
            request_body = _mapping(operation.get("requestBody"))
            if request_body:
                _add_request_body_sources(
                    objects,
                    request_body,
                    key=f"{operation_key}:requestBody",
                    source_path=f"paths.{path}.{method}.requestBody",
                )
            for status, response in _mapping(operation.get("responses")).items():
                _add_response_sources(
                    objects,
                    _mapping(response),
                    key=f"{operation_key}:response:{status}",
                    source_path=f"paths.{path}.{method}.responses.{status}",
                )
            for name, callback in _mapping(operation.get("callbacks")).items():
                objects[f"{operation_key}:callback:{name}"] = source_object(
                    _mapping(callback),
                    source_path=f"paths.{path}.{method}.callbacks.{name}",
                    known_keys=_mapping(callback).keys(),
                )

    for name, webhook in _mapping(document.get("webhooks")).items():
        objects[f"webhook:{name}"] = source_object(
            _mapping(webhook),
            source_path=f"webhooks.{name}",
            known_keys=_mapping(webhook).keys(),
        )

    components = _mapping(document.get("components"))
    for collection in _COMPONENT_COLLECTIONS:
        for name, item in _mapping(components.get(collection)).items():
            value = _mapping(item)
            key = f"component:{collection}:{name}"
            if collection == "parameters":
                _add_parameter_sources(
                    objects,
                    (value,),
                    prefix=key,
                    source_path=f"components.{collection}.{name}",
                    named=True,
                )
            elif collection == "requestBodies":
                _add_request_body_sources(
                    objects,
                    value,
                    key=key,
                    source_path=f"components.{collection}.{name}",
                )
            elif collection == "responses":
                _add_response_sources(
                    objects,
                    value,
                    key=key,
                    source_path=f"components.{collection}.{name}",
                )
            else:
                objects.setdefault(
                    key,
                    source_object(
                        value,
                        source_path=f"components.{collection}.{name}",
                        known_keys=_component_known_keys(collection, value),
                    ),
                )

    codegen = _mapping(document.get("x-codegen"))
    for collection in _CODEGEN_COLLECTIONS:
        for name, item in _mapping(codegen.get(collection)).items():
            value = _mapping(item)
            key = f"x-codegen:{collection}:{name}"
            objects.setdefault(
                key,
                source_object(
                    value,
                    source_path=f"x-codegen.{collection}.{name}",
                    known_keys=_codegen_known_keys(collection, value),
                ),
            )
            if collection in {"entities", "baseEntities"}:
                _add_entity_nested_sources(
                    objects,
                    value,
                    key=key,
                    source_path=f"x-codegen.{collection}.{name}",
                )
            elif collection == "frontends":
                _add_frontend_nested_sources(
                    objects,
                    value,
                    key=key,
                    source_path=f"x-codegen.{collection}.{name}",
                )
            elif collection == "resources":
                _add_resource_nested_sources(
                    objects,
                    value,
                    key=key,
                    source_path=f"x-codegen.{collection}.{name}",
                )

    return replace(view, raw_objects=MappingProxyType(objects))


def _add_parameter_sources(
    objects: dict[str, SourceObject],
    values: Any,
    *,
    prefix: str,
    source_path: str,
    named: bool = False,
) -> None:
    for index, parameter in enumerate(_sequence(values)):
        value = _mapping(parameter)
        identity = str(value.get("name", index)) if named else str(index)
        key = prefix if named else f"{prefix}:{identity}"
        path = source_path if named else f"{source_path}.{index}"
        objects.setdefault(
            key,
            source_object(
                value,
                source_path=path,
                known_keys={
                    "$ref",
                    "name",
                    "in",
                    "description",
                    "required",
                    "deprecated",
                    "allowEmptyValue",
                    "style",
                    "explode",
                    "allowReserved",
                    "schema",
                    "example",
                    "examples",
                    "content",
                },
            ),
        )
        _add_media_sources(
            objects,
            value.get("content"),
            prefix=f"{key}:media",
            source_path=f"{path}.content",
        )


def _add_request_body_sources(
    objects: dict[str, SourceObject],
    value: Mapping[str, Any],
    *,
    key: str,
    source_path: str,
) -> None:
    objects.setdefault(
        key,
        source_object(
            value,
            source_path=source_path,
            known_keys={"$ref", "description", "required", "content"},
        ),
    )
    _add_media_sources(
        objects,
        value.get("content"),
        prefix=f"{key}:media",
        source_path=f"{source_path}.content",
    )


def _add_response_sources(
    objects: dict[str, SourceObject],
    value: Mapping[str, Any],
    *,
    key: str,
    source_path: str,
) -> None:
    objects.setdefault(
        key,
        source_object(
            value,
            source_path=source_path,
            known_keys={"$ref", "description", "headers", "content", "links"},
        ),
    )
    _add_media_sources(
        objects,
        value.get("content"),
        prefix=f"{key}:media",
        source_path=f"{source_path}.content",
    )
    for name, header in _mapping(value.get("headers")).items():
        objects[f"{key}:header:{name}"] = source_object(
            _mapping(header),
            source_path=f"{source_path}.headers.{name}",
            known_keys=_mapping(header).keys(),
        )
    for name, link in _mapping(value.get("links")).items():
        objects[f"{key}:link:{name}"] = source_object(
            _mapping(link),
            source_path=f"{source_path}.links.{name}",
            known_keys=_mapping(link).keys(),
        )


def _add_media_sources(
    objects: dict[str, SourceObject],
    values: Any,
    *,
    prefix: str,
    source_path: str,
) -> None:
    for content_type, media in _mapping(values).items():
        value = _mapping(media)
        key = f"{prefix}:{content_type}"
        objects[key] = source_object(
            value,
            source_path=f"{source_path}.{content_type}",
            known_keys={"schema", "example", "examples", "encoding"},
        )
        for name, encoding in _mapping(value.get("encoding")).items():
            objects[f"{key}:encoding:{name}"] = source_object(
                _mapping(encoding),
                source_path=f"{source_path}.{content_type}.encoding.{name}",
                known_keys={
                    "contentType",
                    "headers",
                    "style",
                    "explode",
                    "allowReserved",
                },
            )


def _add_entity_nested_sources(
    objects: dict[str, SourceObject],
    value: Mapping[str, Any],
    *,
    key: str,
    source_path: str,
) -> None:
    for collection in ("fields", "backendFields", "relations", "constraints", "indexes", "unique"):
        nested = value.get(collection)
        if isinstance(nested, Mapping):
            iterable = nested.items()
        else:
            iterable = enumerate(_sequence(nested))
        for name, item in iterable:
            objects[f"{key}:{collection}:{name}"] = source_object(
                _mapping(item),
                source_path=f"{source_path}.{collection}.{name}",
                known_keys=_mapping(item).keys(),
            )


def _add_frontend_nested_sources(
    objects: dict[str, SourceObject],
    value: Mapping[str, Any],
    *,
    key: str,
    source_path: str,
) -> None:
    for collection in ("components", "screens"):
        nested = value.get(collection)
        if isinstance(nested, Mapping):
            iterable = nested.items()
        else:
            iterable = enumerate(_sequence(nested))
        for name, item in iterable:
            objects[f"{key}:{collection}:{name}"] = source_object(
                _mapping(item),
                source_path=f"{source_path}.{collection}.{name}",
                known_keys=_mapping(item).keys(),
            )


def _add_resource_nested_sources(
    objects: dict[str, SourceObject],
    value: Mapping[str, Any],
    *,
    key: str,
    source_path: str,
) -> None:
    hooks = _mapping(value.get("hooks"))
    for name, hook in hooks.items():
        objects[f"{key}:hook:{name}"] = source_object(
            _mapping(hook),
            source_path=f"{source_path}.hooks.{name}",
            known_keys=_mapping(hook).keys(),
        )


def _operation_key(path: str, method: str, operation: Mapping[str, Any]) -> str:
    operation_id = operation.get("operationId")
    if isinstance(operation_id, str) and operation_id:
        return f"operation:{operation_id}"
    return f"operation:{method}:{path}"


def _component_known_keys(collection: str, value: Mapping[str, Any]) -> set[str]:
    if collection == "securitySchemes":
        return {
            "type",
            "description",
            "name",
            "in",
            "scheme",
            "bearerFormat",
            "flows",
            "openIdConnectUrl",
        }
    if collection == "schemas":
        return set(value.keys())
    return set(value.keys())


def _codegen_known_keys(collection: str, value: Mapping[str, Any]) -> set[str]:
    common = {"id", "name", "description", "info", "notes"}
    known = {
        "resources": common
        | {"route", "path", "tags", "ui", "access", "hooks", "cache"},
        "access": common
        | {"public", "authenticated", "roles", "permissions", "context"},
        "entities": common
        | {
            "resource",
            "schema",
            "store",
            "table",
            "kind",
            "abstract",
            "visibility",
            "extends",
            "fields",
            "backendFields",
            "relations",
            "constraints",
            "indexes",
            "unique",
        },
        "baseEntities": common
        | {
            "resource",
            "schema",
            "kind",
            "abstract",
            "visibility",
            "extends",
            "fields",
            "backendFields",
            "relations",
            "constraints",
            "indexes",
            "unique",
        },
        "frontends": common
        | {
            "title",
            "routePrefix",
            "folders",
            "components",
            "screens",
            "operations",
            "schemas",
        },
    }
    return known.get(collection, set(value.keys()))


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> tuple[Any, ...]:
    return tuple(value) if isinstance(value, list | tuple) else ()
