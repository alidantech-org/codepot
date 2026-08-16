from __future__ import annotations

import json
from typing import Any

import yaml

from .contracts import (
    CacheMode,
    PackInstanceConfig,
    PackSource,
    ProjectConfig,
    ProjectInputSource,
    freeze_object,
)


class ProjectConfigurationError(ValueError):
    def __init__(self, code: str, message: str, *, path: str = "$") -> None:
        super().__init__(f"{path}: {message}")
        self.code = code
        self.message = message
        self.path = path


def load_project(content: bytes, media_type: str) -> ProjectConfig:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProjectConfigurationError("PROJECT_UTF8", "dryv configuration must be UTF-8") from exc
    try:
        if _is_json(media_type):
            document = json.loads(text, object_pairs_hook=_json_pairs)
        elif _is_yaml(media_type):
            document = yaml.load(text, Loader=_UniqueKeyLoader)
        else:
            raise ProjectConfigurationError(
                "PROJECT_MEDIA_TYPE",
                f"unsupported dryv configuration media type {media_type!r}",
            )
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ProjectConfigurationError("PROJECT_SYNTAX", "invalid dryv configuration syntax") from exc
    return decode_project(document)


def decode_project(value: object) -> ProjectConfig:
    root = _object(value, "$")
    _unknown(root, {"apiVersion", "name", "source", "packs", "resources", "cache"}, "$")
    packs_raw = _object(root.get("packs", {}), "$.packs")
    packs: list[PackInstanceConfig] = []
    for name in sorted(packs_raw):
        path = f"$.packs.{name}"
        item = _object(packs_raw[name], path)
        _unknown(item, {"source", "output", "options", "bindings"}, path)
        source_raw = _object(item.get("source"), f"{path}.source")
        _unknown(source_raw, {"local", "git", "ref", "path", "resource"}, f"{path}.source")
        try:
            packs.append(
                PackInstanceConfig(
                    name=name,
                    source=PackSource(
                        local=_optional_string(source_raw.get("local"), f"{path}.source.local"),
                        git=_optional_string(source_raw.get("git"), f"{path}.source.git"),
                        ref=_optional_string(source_raw.get("ref"), f"{path}.source.ref"),
                        path=_optional_string(source_raw.get("path"), f"{path}.source.path"),
                        resource=_optional_string(source_raw.get("resource"), f"{path}.source.resource"),
                    ),
                    output=_string(item.get("output"), f"{path}.output"),
                    options=freeze_object(item.get("options", {}), path=f"{path}.options"),
                    bindings=freeze_object(item.get("bindings", {}), path=f"{path}.bindings"),
                )
            )
        except ValueError as exc:
            raise ProjectConfigurationError("PROJECT_PACK", str(exc), path=path) from exc
    source = _decode_source(root.get("source"))
    try:
        return ProjectConfig(
            api_version=_string(root.get("apiVersion"), "$.apiVersion"),
            name=_string(root.get("name"), "$.name"),
            packs=tuple(packs),
            resources=tuple(
                sorted(_string(item, "$.resources") for item in _list(root.get("resources", []), "$.resources"))
            ),
            cache_mode=CacheMode(_string(root.get("cache", CacheMode.USE.value), "$.cache")),
            source=source,
        )
    except ValueError as exc:
        raise ProjectConfigurationError("PROJECT_INVALID", str(exc)) from exc


def _decode_source(value: object) -> ProjectInputSource | None:
    if value is None:
        return None
    source = _object(value, "$.source")
    _unknown(source, {"ir", "author"}, "$.source")
    try:
        return ProjectInputSource(
            ir=_optional_string(source.get("ir"), "$.source.ir"),
            author=_optional_string(source.get("author"), "$.source.author"),
        )
    except ValueError as exc:
        raise ProjectConfigurationError("PROJECT_SOURCE", str(exc), path="$.source") from exc


def _is_json(media_type: str) -> bool:
    return media_type in {"application/json", "application/dryv+json"} or media_type.endswith("+json")


def _is_yaml(media_type: str) -> bool:
    return media_type in {"application/yaml", "application/x-yaml", "text/yaml", "application/dryv+yaml"} or media_type.endswith("+yaml")


def _object(value: object, path: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ProjectConfigurationError("PROJECT_OBJECT", "expected an object with string keys", path=path)
    return value


def _list(value: object, path: str) -> list[object]:
    if not isinstance(value, list):
        raise ProjectConfigurationError("PROJECT_LIST", "expected a list", path=path)
    return value


def _string(value: object, path: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ProjectConfigurationError("PROJECT_STRING", "expected a non-empty trimmed string", path=path)
    return value


def _optional_string(value: object, path: str) -> str | None:
    return None if value is None else _string(value, path)


def _unknown(value: dict[str, object], allowed: set[str], path: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ProjectConfigurationError("PROJECT_UNKNOWN_FIELD", f"unknown field {unknown[0]!r}", path=path)


def _json_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ProjectConfigurationError("PROJECT_DUPLICATE_KEY", f"duplicate key {key!r}")
        result[key] = value
    return result


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _yaml_mapping(loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict[str, object]:
    result: dict[str, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise ProjectConfigurationError("PROJECT_KEY", "YAML mapping keys must be strings")
        if key in result:
            raise ProjectConfigurationError("PROJECT_DUPLICATE_KEY", f"duplicate key {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _yaml_mapping)

__all__ = ["ProjectConfigurationError", "decode_project", "load_project"]
