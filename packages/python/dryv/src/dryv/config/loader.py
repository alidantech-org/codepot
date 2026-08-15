"""Task-21 compatibility file loaders for Project and Pack Features."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from dryv.features.project import ProjectConfig, ProjectConfigurationError
from dryv.features.project import decode_project as _decode_project

from .pack_loader import PackConfigurationError, PackManifest
from .pack_loader import decode_pack_manifest as _decode_pack_manifest


class ConfigurationError(ValueError):
    def __init__(self, code: str, message: str, *, path: str = "$") -> None:
        super().__init__(f"{path}: {message}")
        self.code = code
        self.path = path
        self.message = message


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict[str, object]:
    result: dict[str, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise ConfigurationError("CFG_NON_STRING_KEY", "mapping keys must be strings")
        if key in result:
            raise ConfigurationError("CFG_DUPLICATE_KEY", f"duplicate key {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def load_project(path: str | Path) -> ProjectConfig:
    return decode_project(_load_document(Path(path)))


def decode_project(value: object) -> ProjectConfig:
    try:
        return _decode_project(value)
    except ProjectConfigurationError as exc:
        raise ConfigurationError(exc.code, exc.message, path=exc.path) from exc


def load_pack_manifest(path: str | Path) -> PackManifest:
    return decode_pack_manifest(_load_document(Path(path)))


def decode_pack_manifest(value: object) -> PackManifest:
    try:
        return _decode_pack_manifest(value)
    except PackConfigurationError as exc:
        raise ConfigurationError(exc.code, exc.message, path=exc.path) from exc


def _load_document(path: Path) -> dict[str, object]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigurationError("CFG_READ_FAILED", "configuration file could not be read", path=str(path)) from exc
    try:
        value = (
            json.loads(text, object_pairs_hook=_json_pairs)
            if path.suffix.lower() == ".json" or text.lstrip().startswith(("{", "["))
            else yaml.load(text, Loader=_UniqueKeyLoader)
        )
    except ConfigurationError:
        raise
    except (json.JSONDecodeError, yaml.YAMLError, UnicodeError, ValueError) as exc:
        raise ConfigurationError("CFG_PARSE_FAILED", "configuration syntax is invalid", path=str(path)) from exc
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ConfigurationError("CFG_EXPECTED_OBJECT", "expected an object")
    return value


def _json_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ConfigurationError("CFG_DUPLICATE_KEY", f"duplicate key {key!r}")
        result[key] = value
    return result


__all__ = [
    "ConfigurationError",
    "decode_pack_manifest",
    "decode_project",
    "load_pack_manifest",
    "load_project",
]
