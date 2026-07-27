from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .models import (
    BindingDefinition,
    OptionDefinition,
    PackInstanceConfig,
    PackManifest,
    PackSource,
    ProjectConfig,
    SelectionConfig,
    SourceConfig,
    freeze_object,
    freeze_value,
)


class ConfigurationError(ValueError):
    def __init__(self, code: str, message: str, *, path: str = "$") -> None:
        super().__init__(f"{path}: {message}")
        self.code = code
        self.path = path
        self.message = message


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_mapping(
    loader: _UniqueKeyLoader,
    node: yaml.MappingNode,
    deep: bool = False,
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise ConfigurationError(
                "CFG_NON_STRING_KEY",
                "mapping keys must be strings",
            )
        if key in result:
            raise ConfigurationError(
                "CFG_DUPLICATE_KEY",
                f"duplicate key {key!r}",
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)


def load_project(path: str | Path) -> ProjectConfig:
    source = Path(path)
    root = _load_document(source)
    return decode_project(root)


def load_pack_manifest(path: str | Path) -> PackManifest:
    source = Path(path)
    root = _load_document(source)
    return decode_pack_manifest(root)


def decode_project(value: object) -> ProjectConfig:
    root = _object(value, "$")
    _unknown(root, {"apiVersion", "name", "sources", "executables", "security", "packs", "commands"}, "$")
    sources_raw = _object(root.get("sources", {}), "$.sources")
    packs_raw = _object(root.get("packs", {}), "$.packs")

    sources: list[SourceConfig] = []
    for name, raw in sources_raw.items():
        item = _object(raw, f"$.sources.{name}")
        _unknown(item, {"adapter", "file", "options"}, f"$.sources.{name}")
        sources.append(
            SourceConfig(
                name=name,
                adapter=_string(item.get("adapter"), f"$.sources.{name}.adapter"),
                file=_string(item.get("file"), f"$.sources.{name}.file"),
                options=freeze_object(item.get("options", {}), path=f"$.sources.{name}.options"),
            )
        )

    packs: list[PackInstanceConfig] = []
    for name, raw in packs_raw.items():
        item = _object(raw, f"$.packs.{name}")
        _unknown(
            item,
            {"source", "input", "output", "options", "bindings", "executables", "commands"},
            f"$.packs.{name}",
        )
        source_raw = _object(item.get("source"), f"$.packs.{name}.source")
        _unknown(source_raw, {"local", "git", "ref", "path"}, f"$.packs.{name}.source")
        packs.append(
            PackInstanceConfig(
                name=name,
                source=PackSource(
                    local=_optional_string(source_raw.get("local"), f"$.packs.{name}.source.local"),
                    git=_optional_string(source_raw.get("git"), f"$.packs.{name}.source.git"),
                    ref=_optional_string(source_raw.get("ref"), f"$.packs.{name}.source.ref"),
                    path=_optional_string(source_raw.get("path"), f"$.packs.{name}.source.path"),
                ),
                input=_optional_string(item.get("input"), f"$.packs.{name}.input"),
                output=_string(item.get("output"), f"$.packs.{name}.output"),
                options=freeze_object(item.get("options", {}), path=f"$.packs.{name}.options"),
                bindings=freeze_object(item.get("bindings", {}), path=f"$.packs.{name}.bindings"),
                executables=freeze_object(item.get("executables", {}), path=f"$.packs.{name}.executables"),
                commands=freeze_object(item.get("commands", {}), path=f"$.packs.{name}.commands"),
            )
        )

    return ProjectConfig(
        api_version=_string(root.get("apiVersion"), "$.apiVersion"),
        name=_string(root.get("name"), "$.name"),
        sources=tuple(sources),
        packs=tuple(packs),
        executables=freeze_object(root.get("executables", {}), path="$.executables"),
        security=freeze_object(root.get("security", {}), path="$.security"),
        commands=freeze_object(root.get("commands", {}), path="$.commands"),
    )


def decode_pack_manifest(value: object) -> PackManifest:
    root = _object(value, "$")
    _unknown(
        root,
        {
            "apiVersion",
            "id",
            "version",
            "description",
            "requires",
            "include",
            "exclude",
            "options",
            "bindings",
            "selections",
            "executables",
            "commands",
        },
        "$",
    )

    options_raw = _object(root.get("options", {}), "$.options")
    options: list[OptionDefinition] = []
    for name, raw in options_raw.items():
        if isinstance(raw, dict):
            _unknown(raw, {"default", "choices", "required", "description"}, f"$.options.{name}")
            choices = tuple(
                freeze_value(item, path=f"$.options.{name}.choices")
                for item in _list(raw.get("choices", []), f"$.options.{name}.choices")
            )
            default = freeze_value(raw.get("default"), path=f"$.options.{name}.default")
            required = _bool(raw.get("required", False), f"$.options.{name}.required")
            description = _optional_string(raw.get("description"), f"$.options.{name}.description")
        else:
            choices = ()
            default = freeze_value(raw, path=f"$.options.{name}")
            required = False
            description = None
        options.append(
            OptionDefinition(
                name=name,
                default=default,
                choices=choices,
                required=required,
                description=description,
            )
        )

    bindings_raw = _object(root.get("bindings", {}), "$.bindings")
    bindings: list[BindingDefinition] = []
    for name, raw in bindings_raw.items():
        item = _object(raw, f"$.bindings.{name}")
        _unknown(item, {"required", "description"}, f"$.bindings.{name}")
        bindings.append(
            BindingDefinition(
                name=name,
                required=_bool(item.get("required", False), f"$.bindings.{name}.required"),
                description=_optional_string(item.get("description"), f"$.bindings.{name}.description"),
            )
        )

    selections_raw = _object(root.get("selections", {}), "$.selections")
    selections: list[SelectionConfig] = []
    for key, raw in selections_raw.items():
        item = _object(raw, f"$.selections.{key}")
        _unknown(
            item,
            {"paths", "select", "imports", "exports", "bindings", "symbols"},
            f"$.selections.{key}",
        )
        imports_raw = _object(item.get("imports", {}), f"$.selections.{key}.imports")
        imports = tuple(
            sorted(
                (
                    local_name,
                    _string(target, f"$.selections.{key}.imports.{local_name}"),
                )
                for local_name, target in imports_raw.items()
            )
        )
        selections.append(
            SelectionConfig(
                key=key,
                paths=tuple(
                    _string(part, f"$.selections.{key}.paths")
                    for part in _list(item.get("paths", []), f"$.selections.{key}.paths")
                ),
                select=_optional_string(item.get("select"), f"$.selections.{key}.select"),
                imports=imports,
                exports=tuple(
                    _string(part, f"$.selections.{key}.exports")
                    for part in _list(item.get("exports", []), f"$.selections.{key}.exports")
                ),
                bindings=tuple(
                    _string(part, f"$.selections.{key}.bindings")
                    for part in _list(item.get("bindings", []), f"$.selections.{key}.bindings")
                ),
                symbols=tuple(
                    _string(part, f"$.selections.{key}.symbols")
                    for part in _list(item.get("symbols", []), f"$.selections.{key}.symbols")
                ),
            )
        )

    return PackManifest(
        api_version=_string(root.get("apiVersion"), "$.apiVersion"),
        id=_string(root.get("id"), "$.id"),
        version=_string(root.get("version"), "$.version"),
        description=_optional_string(root.get("description"), "$.description"),
        include=tuple(
            _string(item, "$.include")
            for item in _list(root.get("include", ["**/*"]), "$.include")
        ),
        exclude=tuple(
            _string(item, "$.exclude")
            for item in _list(root.get("exclude", []), "$.exclude")
        ),
        options=tuple(options),
        bindings=tuple(bindings),
        selections=tuple(selections),
        requires=freeze_object(root.get("requires", {}), path="$.requires"),
        executables=freeze_object(root.get("executables", {}), path="$.executables"),
        commands=freeze_object(root.get("commands", {}), path="$.commands"),
    )


def _load_document(path: Path) -> dict[str, object]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigurationError("CFG_READ_FAILED", "configuration file could not be read", path=str(path)) from exc
    try:
        if path.suffix.lower() == ".json" or text.lstrip().startswith(("{", "[")):
            value = json.loads(text, object_pairs_hook=_json_pairs)
        else:
            value = yaml.load(text, Loader=_UniqueKeyLoader)
    except ConfigurationError:
        raise
    except (json.JSONDecodeError, yaml.YAMLError, UnicodeError, ValueError) as exc:
        raise ConfigurationError("CFG_PARSE_FAILED", "configuration syntax is invalid", path=str(path)) from exc
    return _object(value, "$")


def _json_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ConfigurationError("CFG_DUPLICATE_KEY", f"duplicate key {key!r}")
        result[key] = value
    return result


def _object(value: object, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigurationError("CFG_EXPECTED_OBJECT", "expected an object", path=path)
    if not all(isinstance(key, str) for key in value):
        raise ConfigurationError("CFG_NON_STRING_KEY", "mapping keys must be strings", path=path)
    return value


def _list(value: object, path: str) -> list[object]:
    if not isinstance(value, list):
        raise ConfigurationError("CFG_EXPECTED_LIST", "expected a list", path=path)
    return value


def _string(value: object, path: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ConfigurationError("CFG_EXPECTED_STRING", "expected a non-empty trimmed string", path=path)
    return value


def _optional_string(value: object, path: str) -> str | None:
    if value is None:
        return None
    return _string(value, path)


def _bool(value: object, path: str) -> bool:
    if not isinstance(value, bool):
        raise ConfigurationError("CFG_EXPECTED_BOOLEAN", "expected a boolean", path=path)
    return value


def _unknown(value: dict[str, object], allowed: set[str], path: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ConfigurationError(
            "CFG_UNKNOWN_FIELD",
            f"unknown field {unknown[0]!r}",
            path=path,
        )
