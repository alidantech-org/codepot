from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePosixPath
from typing import TypeAlias

Scalar: TypeAlias = str | int | float | bool | None
FrozenValue: TypeAlias = Scalar | tuple["FrozenValue", ...] | tuple[tuple[str, "FrozenValue"], ...]
FrozenObject: TypeAlias = tuple[tuple[str, FrozenValue], ...]


class PackConfigurationError(ValueError):
    def __init__(self, code: str, message: str, *, path: str = "$") -> None:
        super().__init__(f"{path}: {message}")
        self.code = code
        self.message = message
        self.path = path


class SelectionKind(StrEnum):
    CONTRACT = "contract"
    GROUP = "group"
    PROPERTY = "property"
    SCHEMA = "schema"
    POLICY = "policy"
    FAILURE = "failure"
    EVENT = "event"
    OPERATION = "operation"
    STORAGE_MAPPING = "storage_mapping"
    VALUE_SOURCE = "value_source"
    VIEW = "view"
    WORKFLOW = "workflow"
    PRESENTATION = "presentation"


@dataclass(frozen=True, slots=True)
class OptionDefinition:
    name: str
    default: FrozenValue = None
    choices: tuple[FrozenValue, ...] = ()
    required: bool = False
    description: str | None = None


@dataclass(frozen=True, slots=True)
class BindingDefinition:
    name: str
    required: bool = False
    description: str | None = None


@dataclass(frozen=True, slots=True)
class SelectionDefinition:
    key: str
    kind: SelectionKind
    bindings: tuple[str, ...] = ()
    symbols: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _identifier("selection key", self.key)
        for label, values in (("bindings", self.bindings), ("symbols", self.symbols)):
            if tuple(sorted(set(values))) != values:
                raise PackConfigurationError("PACK_SELECTION_VALUES", f"selection {label} must be sorted and unique")


@dataclass(frozen=True, slots=True)
class TemplateDefinition:
    key: str
    selection: str
    file: str
    renderer: str
    output: str
    depends_on: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _identifier("template key", self.key)
        _identifier("template selection", self.selection)
        _relative_path("template file", self.file)
        if not self.renderer or self.renderer.strip() != self.renderer or any(character.isspace() for character in self.renderer):
            raise PackConfigurationError("PACK_RENDERER", "renderer must be a non-empty capability token")
        _output_pattern(self.output)
        if tuple(sorted(set(self.depends_on))) != self.depends_on:
            raise PackConfigurationError("PACK_TEMPLATE_DEPENDENCIES", "template dependencies must be sorted and unique")


@dataclass(frozen=True, slots=True)
class PackManifest:
    api_version: str
    id: str
    version: str
    description: str | None
    options: tuple[OptionDefinition, ...]
    bindings: tuple[BindingDefinition, ...]
    selections: tuple[SelectionDefinition, ...]
    templates: tuple[TemplateDefinition, ...]
    requires: FrozenObject = ()
    executables: FrozenObject = ()
    commands: FrozenObject = ()

    def __post_init__(self) -> None:
        if self.api_version != "dryv.dev/v1":
            raise PackConfigurationError("PACK_API_VERSION", "pack apiVersion must be dryv.dev/v1")
        _identifier("pack id", self.id)
        if not self.version or self.version.strip() != self.version:
            raise PackConfigurationError("PACK_VERSION", "pack version must be non-empty and trimmed")
        for label, values in (
            ("option", tuple(item.name for item in self.options)),
            ("binding", tuple(item.name for item in self.bindings)),
            ("selection", tuple(item.key for item in self.selections)),
            ("template", tuple(item.key for item in self.templates)),
        ):
            if len(values) != len(set(values)):
                raise PackConfigurationError("PACK_DUPLICATE_ID", f"pack {label} names must be unique")


@dataclass(frozen=True, slots=True)
class ResolvedPack:
    manifest: PackManifest
    options: FrozenObject
    bindings: FrozenObject
    manifest_resource_id: str
    manifest_hash: str


def _identifier(label: str, value: str) -> None:
    if not value or value.strip() != value or any(character.isspace() for character in value):
        raise PackConfigurationError("PACK_IDENTIFIER", f"{label} must be a non-empty identifier")


def _relative_path(label: str, value: str) -> None:
    if not value or value.startswith("/") or "\\" in value:
        raise PackConfigurationError("PACK_PATH", f"{label} must be a POSIX-relative path")
    path = PurePosixPath(value)
    if any(part in {"", ".", ".."} for part in path.parts):
        raise PackConfigurationError("PACK_PATH", f"{label} contains an invalid path segment")


def _output_pattern(value: str) -> None:
    _relative_path("template output", value)
    allowed = {"name", "singular", "plural", "snake", "kebab", "camel", "pascal", "kind"}
    import string

    for _, field_name, format_spec, conversion in string.Formatter().parse(value):
        if field_name is None:
            continue
        if field_name not in allowed or format_spec or conversion:
            raise PackConfigurationError("PACK_OUTPUT_PATTERN", f"unsupported output placeholder {field_name!r}")


__all__ = [
    "BindingDefinition",
    "FrozenObject",
    "FrozenValue",
    "OptionDefinition",
    "PackConfigurationError",
    "PackManifest",
    "ResolvedPack",
    "SelectionDefinition",
    "SelectionKind",
    "TemplateDefinition",
]
