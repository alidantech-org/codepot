"""Compatibility configuration models.

Project usage semantics are owned by :mod:`dryv.features.project`. Pack
manifest semantics remain here until the dedicated Packs Feature migration.
"""

from __future__ import annotations

from dataclasses import dataclass

from dryv.features.project import (
    ConfigScalar,
    PackInstanceConfig,
    PackSource,
    ProjectConfig,
    SourceConfig,
    freeze_object,
    freeze_value,
)
from dryv.ir import FrozenObject, FrozenValue


@dataclass(frozen=True, slots=True)
class OptionDefinition:
    name: str
    default: FrozenValue = None
    choices: tuple[FrozenValue, ...] = ()
    required: bool = False
    description: str | None = None

    def validate(self, value: FrozenValue) -> None:
        if self.choices and value not in self.choices:
            raise ValueError(f"option {self.name!r} must be one of {self.choices!r}")


@dataclass(frozen=True, slots=True)
class BindingDefinition:
    name: str
    required: bool = False
    description: str | None = None


@dataclass(frozen=True, slots=True)
class SelectionConfig:
    key: str
    paths: tuple[str, ...] = ()
    select: str | None = None
    imports: tuple[tuple[str, str], ...] = ()
    exports: tuple[str, ...] = ()
    bindings: tuple[str, ...] = ()
    symbols: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_id("selection key", self.key)
        for part in self.paths:
            _require_path_segment("selection path", part)
        if self.select is not None and (not self.select or self.select.strip() != self.select):
            raise ValueError("selection selector must be a non-empty trimmed string")
        import_names = tuple(name for name, _ in self.imports)
        if tuple(sorted(import_names)) != import_names or len(import_names) != len(set(import_names)):
            raise ValueError("selection imports must be sorted by unique local name")
        for label, values in (("selection exports", self.exports), ("selection bindings", self.bindings)):
            if len(values) != len(set(values)):
                raise ValueError(f"{label} must be unique")


@dataclass(frozen=True, slots=True)
class PackManifest:
    api_version: str
    id: str
    version: str
    description: str | None
    include: tuple[str, ...]
    exclude: tuple[str, ...]
    options: tuple[OptionDefinition, ...]
    bindings: tuple[BindingDefinition, ...]
    selections: tuple[SelectionConfig, ...]
    requires: FrozenObject = ()
    executables: FrozenObject = ()
    commands: FrozenObject = ()

    def __post_init__(self) -> None:
        if self.api_version != "dryv.dev/v1":
            raise ValueError("pack apiVersion must be dryv.dev/v1")
        if not self.id or self.id.strip() != self.id:
            raise ValueError("pack id must be a non-empty trimmed string")
        if not self.version or self.version.strip() != self.version:
            raise ValueError("pack version must be a non-empty trimmed string")
        for label, values in (
            ("pack option names", tuple(item.name for item in self.options)),
            ("pack binding names", tuple(item.name for item in self.bindings)),
            ("pack selection keys", tuple(item.key for item in self.selections)),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"{label} must be unique")

    def selection(self, key: str) -> SelectionConfig | None:
        return next((item for item in self.selections if item.key == key), None)

    def resolve_options(self, authored: FrozenObject) -> FrozenObject:
        definitions = {item.name: item for item in self.options}
        provided = dict(authored)
        unknown = sorted(set(provided) - set(definitions))
        if unknown:
            raise ValueError(f"unknown pack option {unknown[0]!r}")
        resolved: list[tuple[str, FrozenValue]] = []
        for name in sorted(definitions):
            definition = definitions[name]
            if name in provided:
                value = provided[name]
            elif definition.required and definition.default is None:
                raise ValueError(f"required pack option {name!r} is missing")
            else:
                value = definition.default
            definition.validate(value)
            resolved.append((name, value))
        return tuple(resolved)

    def validate_bindings(self, authored: FrozenObject) -> None:
        definitions = {item.name: item for item in self.bindings}
        provided = set(dict(authored))
        unknown = sorted(provided - set(definitions))
        if unknown:
            raise ValueError(f"unknown pack binding {unknown[0]!r}")
        missing = sorted(name for name, definition in definitions.items() if definition.required and name not in provided)
        if missing:
            raise ValueError(f"required pack binding {missing[0]!r} is missing")


def _require_id(label: str, value: str) -> None:
    if not value or value.strip() != value or any(character.isspace() for character in value):
        raise ValueError(f"{label} must be a non-empty identifier")


def _require_path_segment(label: str, value: str) -> None:
    if not value or "/" in value or "\\" in value or value in {".", ".."}:
        raise ValueError(f"{label} values must be path segments")


__all__ = [
    "BindingDefinition",
    "ConfigScalar",
    "OptionDefinition",
    "PackInstanceConfig",
    "PackManifest",
    "PackSource",
    "ProjectConfig",
    "SelectionConfig",
    "SourceConfig",
    "freeze_object",
    "freeze_value",
]
