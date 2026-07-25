from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from types import MappingProxyType
from typing import Any

from contracts.normalized import SourceObject, source_object
from contracts.normalized_api import NormalizedApiView


def extend_normalized_source_registry(
    view: NormalizedApiView,
    raw: Mapping[str, Any] | None,
) -> NormalizedApiView:
    """Register every supported OpenAPI and x-codegen source object by stable key."""

    document = _mapping(raw)
    objects = dict(view.raw_objects)
    _add_info(objects, document)
    _add_servers(objects, document)
    _add_paths(objects, document)
    _add_components(objects, document)
    _add_codegen(objects, document)
    return replace(view, raw_objects=MappingProxyType(objects))


def _add_info(objects: dict[str, SourceObject], document: Mapping[str, Any]) -> None:
    raw = _mapping(document.get("info"))
    if raw:
        objects["info"] = source_object(
            raw,
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
        )


def _add_servers(objects: dict[str, SourceObject], document: Mapping[str, Any]) -> None:
    for index, value in enumerate(_sequence(document.get("servers"))):
        raw = _mapping(value)
        key = f"server:{index}"
        objects[key] = source_object(
            raw,
            source_path=f"servers.{index}",
            known_keys={"url", "description", "variables"},
        )
        for name, variable in _mapping(raw.get("variables")).items():
            objects[f"{key}:variable:{name}"] = source_object(
                _mapping(variable),
                source_path=f"servers.{index}.variables.{name}",
                known_keys={"enum", "default", "description"},
            )


def _add_paths(objects: dict[str, SourceObject], document: Mapping[str, Any]) -> None:
    for path, value in _mapping(document.get("paths")).items():
        raw_path = _mapping(value)
        path_key = f"path:{path}"
        objects[path_key] = source_object(
            raw_path,
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
        )
        _add_parameters(
            objects,
            raw_path.get("parameters"),
            prefix=f"{path_key}:parameter",
            source_path=f"paths.{path}.parameters",
        )
        for method in _HTTP_METHODS:
            operation = _mapping(raw_path.get(method))
            if not operation:
                continue
            operation_id = operation.get("operationId")
            operation_key = (
                f"operation:{operation_id}"
                if isinstance(operation_id, str) and operation_id
                else f"operation:{method}:{path}"
            )
            objects[operation_key] = source_object(
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
            )
            _add_parameters(
                objects,
                operation.get("parameters"),
                prefix=f"{operation_key}:parameter",
                source_path=f"paths.{path}.{method}.parameters",
            )
            request_body = _mapping(operation.get("requestBody"))
            if request_body:
                _add_request_body(
                    objects,
                    request_body,
                    key=f"{operation_key}:requestBody",
                    source_path=f"paths.{path}.{method}.requestBody",
                )
            for status, response in _mapping(operation.get("responses")).items():
                _add_response(
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


def _add_components(
    objects: dict[str, SourceObject],
    document: Mapping[str, Any],
) -> None:
    components = _mapping(document.get("components"))
    for collection in _COMPONENT_COLLECTIONS:
        for name, value in _mapping(components.get(collection)).items():
            raw = _mapping(value)
            key = f"component:{collection}:{name}"
            if collection == "parameters":
                objects[key] = source_object(
                    raw,
                    source_path=f"components.parameters.{name}",
                    known_keys=_PARAMETER_KEYS,
                )
            elif collection == "requestBodies":
                _add_request_body(
                    objects,
                    raw,
                    key=key,
                    source_path=f"components.requestBodies.{name}",
                )
            elif collection == "responses":
                _add_response(
                    objects,
                    raw,
                    key=key,
                    source_path=f"components.responses.{name}",
                )
            else:
                objects[key] = source_object(
                    raw,
                    source_path=f"components.{collection}.{name}",
                    known_keys=raw.keys(),
                )


def _add_codegen(objects: dict[str, SourceObject], document: Mapping[str, Any]) -> None:
    codegen = _mapping(document.get("x-codegen"))
    for collection in _CODEGEN_COLLECTIONS:
        for name, value in _mapping(codegen.get(collection)).items():
            raw = _mapping(value)
            key = f"x-codegen:{collection}:{name}"
            known = (
                _FRONTEND_KEYS
                if collection == "frontends"
                else raw.keys()
            )
            objects[key] = source_object(
                raw,
                source_path=f"x-codegen.{collection}.{name}",
                known_keys=known,
            )
            if collection in {"entities", "baseEntities"}:
                _add_named_nested(
                    objects,
                    raw,
                    collections=(
                        "fields",
                        "backendFields",
                        "relations",
                        "constraints",
                        "indexes",
                        "unique",
                    ),
                    prefix=key,
                    source_path=f"x-codegen.{collection}.{name}",
                )
            elif collection == "frontends":
                _add_named_nested(
                    objects,
                    raw,
                    collections=("components", "screens"),
                    prefix=key,
                    source_path=f"x-codegen.frontends.{name}",
                )
            elif collection == "resources":
                for hook_name, hook in _mapping(raw.get("hooks")).items():
                    objects[f"{key}:hook:{hook_name}"] = source_object(
                        _mapping(hook),
                        source_path=f"x-codegen.resources.{name}.hooks.{hook_name}",
                        known_keys=_mapping(hook).keys(),
                    )


def _add_named_nested(
    objects: dict[str, SourceObject],
    raw: Mapping[str, Any],
    *,
    collections: tuple[str, ...],
    prefix: str,
    source_path: str,
) -> None:
    for collection in collections:
        nested = raw.get(collection)
        iterable = (
            tuple(_mapping(nested).items())
            if isinstance(nested, Mapping)
            else tuple(
                (str(_mapping(item).get("name", index)), item)
                for index, item in enumerate(_sequence(nested))
            )
        )
        for name, value in iterable:
            objects[f"{prefix}:{collection}:{name}"] = source_object(
                _mapping(value),
                source_path=f"{source_path}.{collection}.{name}",
                known_keys=_mapping(value).keys(),
            )


def _add_parameters(
    objects: dict[str, SourceObject],
    value: Any,
    *,
    prefix: str,
    source_path: str,
) -> None:
    for index, parameter in enumerate(_sequence(value)):
        raw = _mapping(parameter)
        key = f"{prefix}:{index}"
        objects[key] = source_object(
            raw,
            source_path=f"{source_path}.{index}",
            known_keys=_PARAMETER_KEYS,
        )
        _add_media(
            objects,
            raw.get("content"),
            prefix=f"{key}:media",
            source_path=f"{source_path}.{index}.content",
        )


def _add_request_body(
    objects: dict[str, SourceObject],
    raw: Mapping[str, Any],
    *,
    key: str,
    source_path: str,
) -> None:
    objects[key] = source_object(
        raw,
        source_path=source_path,
        known_keys={"$ref", "description", "required", "content"},
    )
    _add_media(
        objects,
        raw.get("content"),
        prefix=f"{key}:media",
        source_path=f"{source_path}.content",
    )


def _add_response(
    objects: dict[str, SourceObject],
    raw: Mapping[str, Any],
    *,
    key: str,
    source_path: str,
) -> None:
    objects[key] = source_object(
        raw,
        source_path=source_path,
        known_keys={"$ref", "description", "headers", "content", "links"},
    )
    _add_media(
        objects,
        raw.get("content"),
        prefix=f"{key}:media",
        source_path=f"{source_path}.content",
    )
    for name, value in _mapping(raw.get("headers")).items():
        objects[f"{key}:header:{name}"] = source_object(
            _mapping(value),
            source_path=f"{source_path}.headers.{name}",
            known_keys=_mapping(value).keys(),
        )
    for name, value in _mapping(raw.get("links")).items():
        objects[f"{key}:link:{name}"] = source_object(
            _mapping(value),
            source_path=f"{source_path}.links.{name}",
            known_keys=_mapping(value).keys(),
        )


def _add_media(
    objects: dict[str, SourceObject],
    value: Any,
    *,
    prefix: str,
    source_path: str,
) -> None:
    for content_type, media in _mapping(value).items():
        raw = _mapping(media)
        objects[f"{prefix}:{content_type}"] = source_object(
            raw,
            source_path=f"{source_path}.{content_type}",
            known_keys={"schema", "example", "examples", "encoding"},
        )


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> tuple[Any, ...]:
    return tuple(value) if isinstance(value, list | tuple) else ()


_HTTP_METHODS = ("get", "put", "post", "delete", "patch", "options", "head", "trace")
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
_PARAMETER_KEYS = {
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
}
_FRONTEND_KEYS = {
    "name",
    "title",
    "description",
    "route",
    "routePrefix",
    "components",
    "screens",
    "info",
    "notes",
}
