from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from typing import Any

import yaml

from .contracts import (
    BindingDefinition,
    FrozenObject,
    FrozenValue,
    OptionDefinition,
    PackConfigurationError,
    PackManifest,
    SelectionDefinition,
    SelectionKind,
    TemplateDefinition,
)

_MAX_VALUE_DEPTH = 64
_MAX_VALUE_ITEMS = 100_000


@dataclass(slots=True)
class _FreezeState:
    active: set[int] = field(default_factory=set)
    items: int = 0


def load_pack_manifest(content: bytes, media_type: str) -> PackManifest:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PackConfigurationError("PACK_UTF8", "pack manifest must be UTF-8") from exc
    try:
        if media_type in {"application/json", "application/dryv-pack+json"} or media_type.endswith("+json"):
            document = json.loads(text, object_pairs_hook=_json_pairs)
        elif media_type in {"application/yaml", "application/x-yaml", "text/yaml", "application/dryv-pack+yaml"} or media_type.endswith("+yaml"):
            document = yaml.load(text, Loader=_UniqueKeyLoader)
        else:
            raise PackConfigurationError("PACK_MEDIA_TYPE", f"unsupported pack manifest media type {media_type!r}")
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise PackConfigurationError("PACK_SYNTAX", "invalid pack manifest syntax") from exc
    return decode_pack_manifest(document)


def decode_pack_manifest(value: object) -> PackManifest:
    root = _object(value, "$")
    _unknown(root, {"apiVersion", "id", "version", "description", "options", "bindings", "selections", "templates", "requires", "executables", "commands"}, "$")

    options: list[OptionDefinition] = []
    for name, raw in sorted(_object(root.get("options", {}), "$.options").items()):
        path = f"$.options.{name}"
        item = _object(raw, path)
        _unknown(item, {"default", "choices", "required", "description"}, path)
        options.append(
            OptionDefinition(
                name,
                _freeze(item.get("default"), f"{path}.default"),
                tuple(_freeze(choice, f"{path}.choices") for choice in _list(item.get("choices", []), f"{path}.choices")),
                _bool(item.get("required", False), f"{path}.required"),
                _optional_string(item.get("description"), f"{path}.description"),
            )
        )

    bindings: list[BindingDefinition] = []
    for name, raw in sorted(_object(root.get("bindings", {}), "$.bindings").items()):
        path = f"$.bindings.{name}"
        item = _object(raw, path)
        _unknown(item, {"required", "description"}, path)
        bindings.append(BindingDefinition(name, _bool(item.get("required", False), f"{path}.required"), _optional_string(item.get("description"), f"{path}.description")))

    selections: list[SelectionDefinition] = []
    for key, raw in sorted(_object(root.get("selections", {}), "$.selections").items()):
        path = f"$.selections.{key}"
        item = _object(raw, path)
        _unknown(item, {"kind", "bindings", "symbols"}, path)
        try:
            kind = SelectionKind(_string(item.get("kind"), f"{path}.kind"))
        except ValueError as exc:
            raise PackConfigurationError("PACK_SELECTION_KIND", "unknown canonical selection kind", path=f"{path}.kind") from exc
        selections.append(
            SelectionDefinition(
                key,
                kind,
                tuple(sorted(_string(value, f"{path}.bindings") for value in _list(item.get("bindings", []), f"{path}.bindings"))),
                tuple(sorted(_string(value, f"{path}.symbols") for value in _list(item.get("symbols", []), f"{path}.symbols"))),
            )
        )

    templates: list[TemplateDefinition] = []
    for key, raw in sorted(_object(root.get("templates", {}), "$.templates").items()):
        path = f"$.templates.{key}"
        item = _object(raw, path)
        _unknown(item, {"selection", "file", "renderer", "output", "dependsOn"}, path)
        templates.append(
            TemplateDefinition(
                key,
                _string(item.get("selection"), f"{path}.selection"),
                _string(item.get("file"), f"{path}.file"),
                _string(item.get("renderer"), f"{path}.renderer"),
                _string(item.get("output"), f"{path}.output"),
                tuple(sorted(_string(value, f"{path}.dependsOn") for value in _list(item.get("dependsOn", []), f"{path}.dependsOn"))),
            )
        )

    return PackManifest(
        _string(root.get("apiVersion"), "$.apiVersion"),
        _string(root.get("id"), "$.id"),
        _string(root.get("version"), "$.version"),
        _optional_string(root.get("description"), "$.description"),
        tuple(options),
        tuple(bindings),
        tuple(selections),
        tuple(templates),
        _freeze_object(root.get("requires", {}), "$.requires"),
        _freeze_object(root.get("executables", {}), "$.executables"),
        _freeze_object(root.get("commands", {}), "$.commands"),
    )


def _freeze(value: object, path: str) -> FrozenValue:
    return _freeze_value(value, path=path, depth=0, state=_FreezeState())


def _freeze_value(value: object, *, path: str, depth: int, state: _FreezeState) -> FrozenValue:
    state.items += 1
    if state.items > _MAX_VALUE_ITEMS:
        raise PackConfigurationError(
            "PACK_VALUE_LIMIT",
            f"pack value exceeds {_MAX_VALUE_ITEMS} items",
            path=path,
        )
    if depth > _MAX_VALUE_DEPTH:
        raise PackConfigurationError(
            "PACK_VALUE_DEPTH",
            f"pack value exceeds depth {_MAX_VALUE_DEPTH}",
            path=path,
        )
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise PackConfigurationError(
                "PACK_NUMBER",
                "non-finite numbers are not supported",
                path=path,
            )
        return value
    if isinstance(value, (list, dict)):
        identity = id(value)
        if identity in state.active:
            raise PackConfigurationError(
                "PACK_VALUE_RECURSIVE",
                "recursive pack values are not supported",
                path=path,
            )
        state.active.add(identity)
        try:
            if isinstance(value, list):
                return tuple(
                    _freeze_value(
                        item,
                        path=f"{path}[{index}]",
                        depth=depth + 1,
                        state=state,
                    )
                    for index, item in enumerate(value)
                )
            if not all(isinstance(key, str) and key for key in value):
                raise PackConfigurationError(
                    "PACK_KEY",
                    "pack object keys must be non-empty strings",
                    path=path,
                )
            return tuple(
                (
                    key,
                    _freeze_value(
                        value[key],
                        path=f"{path}.{key}",
                        depth=depth + 1,
                        state=state,
                    ),
                )
                for key in sorted(value)
            )
        finally:
            state.active.remove(identity)
    raise PackConfigurationError("PACK_VALUE", f"unsupported pack value {type(value).__name__}", path=path)


def _freeze_object(value: object, path: str) -> FrozenObject:
    frozen = _freeze(value, path)
    if not isinstance(frozen, tuple) or (frozen and not all(isinstance(item, tuple) and len(item) == 2 for item in frozen)):
        raise PackConfigurationError("PACK_OBJECT", "expected an object", path=path)
    return frozen  # type: ignore[return-value]


def _object(value: object, path: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise PackConfigurationError("PACK_OBJECT", "expected an object with string keys", path=path)
    return value


def _list(value: object, path: str) -> list[object]:
    if not isinstance(value, list):
        raise PackConfigurationError("PACK_LIST", "expected a list", path=path)
    return value


def _string(value: object, path: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise PackConfigurationError("PACK_STRING", "expected a non-empty trimmed string", path=path)
    return value


def _optional_string(value: object, path: str) -> str | None:
    return None if value is None else _string(value, path)


def _bool(value: object, path: str) -> bool:
    if not isinstance(value, bool):
        raise PackConfigurationError("PACK_BOOLEAN", "expected a boolean", path=path)
    return value


def _unknown(value: dict[str, object], allowed: set[str], path: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise PackConfigurationError("PACK_UNKNOWN_FIELD", f"unknown field {unknown[0]!r}", path=path)


def _json_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise PackConfigurationError("PACK_DUPLICATE_KEY", f"duplicate key {key!r}")
        result[key] = value
    return result


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _yaml_mapping(loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict[str, object]:
    result: dict[str, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise PackConfigurationError("PACK_KEY", "YAML mapping keys must be strings")
        if key in result:
            raise PackConfigurationError("PACK_DUPLICATE_KEY", f"duplicate key {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _yaml_mapping)

__all__ = ["decode_pack_manifest", "load_pack_manifest"]
