from __future__ import annotations

from typing import Any

from .models import BuildMode, CacheMode, PackInstanceConfig, PackSource, ProjectConfig, SourceConfig, freeze_object


class ProjectConfigurationError(ValueError):
    def __init__(self, code: str, message: str, *, path: str = "$") -> None:
        super().__init__(f"{path}: {message}")
        self.code = code
        self.path = path
        self.message = message


def decode_project(value: object) -> ProjectConfig:
    root = _object(value, "$")
    _unknown(root, {"apiVersion", "name", "sources", "executables", "security", "packs", "commands", "bindings", "resources", "cache", "build", "renderers"}, "$")
    sources_raw = _object(root.get("sources", {}), "$.sources")
    packs_raw = _object(root.get("packs", {}), "$.packs")

    sources: list[SourceConfig] = []
    for name in sorted(sources_raw):
        item = _object(sources_raw[name], f"$.sources.{name}")
        _unknown(item, {"adapter", "file", "resource", "author", "resources", "options"}, f"$.sources.{name}")
        try:
            sources.append(SourceConfig(
                name=name,
                adapter=_optional_string(item.get("adapter"), f"$.sources.{name}.adapter"),
                file=_optional_string(item.get("file"), f"$.sources.{name}.file"),
                resource=_optional_string(item.get("resource"), f"$.sources.{name}.resource"),
                author=_optional_string(item.get("author"), f"$.sources.{name}.author"),
                resources=tuple(sorted(_string(entry, f"$.sources.{name}.resources") for entry in _list(item.get("resources", []), f"$.sources.{name}.resources"))),
                options=freeze_object(item.get("options", {}), path=f"$.sources.{name}.options"),
            ))
        except ValueError as exc:
            raise ProjectConfigurationError("PROJECT_INVALID_SOURCE", str(exc), path=f"$.sources.{name}") from exc

    packs: list[PackInstanceConfig] = []
    for name in sorted(packs_raw):
        item = _object(packs_raw[name], f"$.packs.{name}")
        _unknown(item, {"source", "input", "output", "options", "bindings", "executables", "commands"}, f"$.packs.{name}")
        source_raw = _object(item.get("source"), f"$.packs.{name}.source")
        _unknown(source_raw, {"local", "git", "ref", "path", "resource"}, f"$.packs.{name}.source")
        try:
            packs.append(PackInstanceConfig(
                name=name,
                source=PackSource(
                    local=_optional_string(source_raw.get("local"), f"$.packs.{name}.source.local"),
                    git=_optional_string(source_raw.get("git"), f"$.packs.{name}.source.git"),
                    ref=_optional_string(source_raw.get("ref"), f"$.packs.{name}.source.ref"),
                    path=_optional_string(source_raw.get("path"), f"$.packs.{name}.source.path"),
                    resource=_optional_string(source_raw.get("resource"), f"$.packs.{name}.source.resource"),
                ),
                input=_optional_string(item.get("input"), f"$.packs.{name}.input"),
                output=_string(item.get("output"), f"$.packs.{name}.output"),
                options=freeze_object(item.get("options", {}), path=f"$.packs.{name}.options"),
                bindings=freeze_object(item.get("bindings", {}), path=f"$.packs.{name}.bindings"),
                executables=freeze_object(item.get("executables", {}), path=f"$.packs.{name}.executables"),
                commands=freeze_object(item.get("commands", {}), path=f"$.packs.{name}.commands"),
            ))
        except ValueError as exc:
            raise ProjectConfigurationError("PROJECT_INVALID_PACK", str(exc), path=f"$.packs.{name}") from exc

    try:
        return ProjectConfig(
            api_version=_string(root.get("apiVersion"), "$.apiVersion"),
            name=_string(root.get("name"), "$.name"),
            sources=tuple(sources),
            packs=tuple(packs),
            executables=freeze_object(root.get("executables", {}), path="$.executables"),
            security=freeze_object(root.get("security", {}), path="$.security"),
            commands=freeze_object(root.get("commands", {}), path="$.commands"),
            bindings=freeze_object(root.get("bindings", {}), path="$.bindings"),
            resources=tuple(sorted(_string(item, "$.resources") for item in _list(root.get("resources", []), "$.resources"))),
            cache_mode=CacheMode(_string(root.get("cache", CacheMode.USE.value), "$.cache")),
            build_mode=BuildMode(_string(root.get("build", BuildMode.RENDER.value), "$.build")),
            renderers=freeze_object(root.get("renderers", {}), path="$.renderers"),
        )
    except ValueError as exc:
        raise ProjectConfigurationError("PROJECT_INVALID", str(exc)) from exc


def _object(value: object, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProjectConfigurationError("PROJECT_EXPECTED_OBJECT", "expected an object", path=path)
    if not all(isinstance(key, str) for key in value):
        raise ProjectConfigurationError("PROJECT_NON_STRING_KEY", "mapping keys must be strings", path=path)
    return value


def _list(value: object, path: str) -> list[object]:
    if not isinstance(value, list):
        raise ProjectConfigurationError("PROJECT_EXPECTED_LIST", "expected a list", path=path)
    return value


def _string(value: object, path: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ProjectConfigurationError("PROJECT_EXPECTED_STRING", "expected a non-empty trimmed string", path=path)
    return value


def _optional_string(value: object, path: str) -> str | None:
    return None if value is None else _string(value, path)


def _unknown(value: dict[str, object], allowed: set[str], path: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ProjectConfigurationError("PROJECT_UNKNOWN_FIELD", f"unknown field {unknown[0]!r}", path=path)


__all__ = ["ProjectConfigurationError", "decode_project"]
