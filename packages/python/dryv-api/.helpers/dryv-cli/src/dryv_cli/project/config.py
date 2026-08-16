from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import yaml

from .project import ProjectError


@dataclass(frozen=True, slots=True)
class PackLocator:
    name: str
    output: str
    local: str | None = None
    git: str | None = None
    ref: str | None = None
    path: str | None = None
    resource: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectLocators:
    source_ir: str | None
    source_author: str | None
    packs: tuple[PackLocator, ...]
    resources: tuple[str, ...]


def load_locators(content: bytes, media_type: str) -> ProjectLocators:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProjectError("CLI_PROJECT_UTF8", "dryv.yaml must be UTF-8") from exc
    try:
        if media_type.endswith("json"):
            document = json.loads(text, object_pairs_hook=_json_pairs)
        else:
            document = yaml.load(text, Loader=_UniqueKeyLoader)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ProjectError("CLI_PROJECT_SYNTAX", "dryv.yaml could not be parsed") from exc
    if not isinstance(document, dict):
        raise ProjectError("CLI_PROJECT_ROOT", "dryv.yaml root must be an object")

    source_ir, source_author = _source(document.get("source"))
    packs = _packs(document.get("packs", {}))
    resources_raw = document.get("resources", [])
    if not isinstance(resources_raw, list) or not all(
        isinstance(item, str) for item in resources_raw
    ):
        raise ProjectError("CLI_PROJECT_RESOURCES", "resources must be an array of resource ids")
    if len(resources_raw) != len(set(resources_raw)):
        raise ProjectError("CLI_PROJECT_RESOURCES", "resources must be unique")
    return ProjectLocators(source_ir, source_author, packs, tuple(sorted(resources_raw)))


def _source(value: object) -> tuple[str | None, str | None]:
    if value is None:
        return None, None
    if not isinstance(value, dict):
        raise ProjectError("CLI_PROJECT_SOURCE", "source must be an object")
    ir = _optional_string(value.get("ir"), "source.ir")
    author = _optional_string(value.get("author"), "source.author")
    if (ir is None) == (author is None):
        raise ProjectError("CLI_PROJECT_SOURCE", "source requires exactly one of ir or author")
    return ir, author


def _packs(value: object) -> tuple[PackLocator, ...]:
    if not isinstance(value, dict):
        raise ProjectError("CLI_PROJECT_PACKS", "packs must be an object")
    result: list[PackLocator] = []
    for name in sorted(value):
        item = value[name]
        if not isinstance(name, str) or not name:
            raise ProjectError("CLI_PROJECT_PACK", "pack names must be non-empty strings")
        if not isinstance(item, dict):
            raise ProjectError("CLI_PROJECT_PACK", f"pack {name!r} must be an object")
        source = item.get("source")
        if not isinstance(source, dict):
            raise ProjectError("CLI_PROJECT_PACK", f"pack {name!r} requires a source object")
        local = _optional_string(source.get("local"), f"packs.{name}.source.local")
        git = _optional_string(source.get("git"), f"packs.{name}.source.git")
        resource = _optional_string(source.get("resource"), f"packs.{name}.source.resource")
        ref = _optional_string(source.get("ref"), f"packs.{name}.source.ref")
        path = _optional_string(source.get("path"), f"packs.{name}.source.path")
        if sum(item is not None for item in (local, git, resource)) != 1:
            raise ProjectError(
                "CLI_PROJECT_PACK_SOURCE",
                f"pack {name!r} requires exactly one of source.local, source.git or source.resource",
            )
        if git is not None and ref is None:
            raise ProjectError(
                "CLI_PROJECT_PACK_REF", f"Git pack {name!r} requires an explicit source.ref"
            )
        if git is None and (ref is not None or path is not None):
            raise ProjectError(
                "CLI_PROJECT_PACK_SOURCE",
                f"pack {name!r} may use source.ref/source.path only with source.git",
            )
        result.append(
            PackLocator(
                name=name,
                output=_string(item.get("output"), f"packs.{name}.output"),
                local=local,
                git=git,
                ref=ref,
                path=path,
                resource=resource,
            )
        )
    return tuple(result)


def _string(value: object, path: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ProjectError("CLI_PROJECT_STRING", f"{path} must be a non-empty trimmed string")
    return value


def _optional_string(value: object, path: str) -> str | None:
    return None if value is None else _string(value, path)


def _json_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ProjectError("CLI_PROJECT_DUPLICATE_KEY", f"duplicate project key {key!r}")
        result[key] = value
    return result


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _yaml_mapping(
    loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise ProjectError("CLI_PROJECT_KEY", "YAML project mapping keys must be strings")
        if key in result:
            raise ProjectError("CLI_PROJECT_DUPLICATE_KEY", f"duplicate project key {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _yaml_mapping)

__all__ = ["PackLocator", "ProjectLocators", "load_locators"]
