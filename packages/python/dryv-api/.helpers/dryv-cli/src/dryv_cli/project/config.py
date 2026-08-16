from __future__ import annotations

import json
from dataclasses import dataclass

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
        document = json.loads(text) if media_type.endswith("json") else yaml.safe_load(text)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ProjectError("CLI_PROJECT_SYNTAX", "dryv.yaml could not be parsed") from exc
    if not isinstance(document, dict):
        raise ProjectError("CLI_PROJECT_ROOT", "dryv.yaml root must be an object")

    source_ir, source_author = _source(document.get("source"))
    packs = _packs(document.get("packs", {}))
    resources_raw = document.get("resources", [])
    if not isinstance(resources_raw, list) or not all(isinstance(item, str) for item in resources_raw):
        raise ProjectError("CLI_PROJECT_RESOURCES", "resources must be an array of resource ids")
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
        result.append(
            PackLocator(
                name=name,
                output=_string(item.get("output"), f"packs.{name}.output"),
                local=_optional_string(source.get("local"), f"packs.{name}.source.local"),
                git=_optional_string(source.get("git"), f"packs.{name}.source.git"),
                ref=_optional_string(source.get("ref"), f"packs.{name}.source.ref"),
                path=_optional_string(source.get("path"), f"packs.{name}.source.path"),
                resource=_optional_string(source.get("resource"), f"packs.{name}.source.resource"),
            )
        )
    return tuple(result)


def _string(value: object, path: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ProjectError("CLI_PROJECT_STRING", f"{path} must be a non-empty trimmed string")
    return value


def _optional_string(value: object, path: str) -> str | None:
    return None if value is None else _string(value, path)


__all__ = ["PackLocator", "ProjectLocators", "load_locators"]
