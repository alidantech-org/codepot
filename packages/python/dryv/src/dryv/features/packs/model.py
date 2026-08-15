from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(frozen=True, slots=True)
class OptionDefinition:
    name: str
    default: FrozenValue = None
    choices: tuple[FrozenValue, ...] = ()
    required: bool = False
    description: str | None = None

    def validate(self, value: FrozenValue) -> None:
        if self.choices and value not in self.choices:
            raise PackConfigurationError("PACK_OPTION_CHOICE", f"option {self.name!r} must be one of {self.choices!r}")


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
        _identifier("selection key", self.key)
        if any(not part or part in {".", ".."} or "/" in part or "\\" in part for part in self.paths):
            raise PackConfigurationError("PACK_OUTPUT_PATH", "selection paths must contain safe relative segments")
        if self.select is not None and (not self.select or self.select.strip() != self.select):
            raise PackConfigurationError("PACK_SELECTOR", "selector must be a non-empty trimmed string")
        names = tuple(name for name, _ in self.imports)
        if tuple(sorted(names)) != names or len(names) != len(set(names)):
            raise PackConfigurationError("PACK_IMPORTS", "selection imports must be sorted by unique local name")
        for label, values in (("exports", self.exports), ("bindings", self.bindings), ("symbols", self.symbols)):
            if len(values) != len(set(values)):
                raise PackConfigurationError("PACK_DUPLICATE_VALUE", f"selection {label} must be unique")


@dataclass(frozen=True, slots=True)
class PackTemplateResource:
    resource_id: str
    relative_path: str
    media_type: str
    renderer_capability: str
    selection_key: str | None = None

    def __post_init__(self) -> None:
        for label, value in (
            ("resource id", self.resource_id),
            ("relative path", self.relative_path),
            ("media type", self.media_type),
            ("renderer capability", self.renderer_capability),
        ):
            if not value or value.strip() != value:
                raise PackConfigurationError("PACK_TEMPLATE_RESOURCE", f"template {label} must be non-empty and trimmed")
        if self.relative_path.startswith(("/", "\\")) or ".." in self.relative_path.replace("\\", "/").split("/"):
            raise PackConfigurationError("PACK_TEMPLATE_PATH", "template resource paths must be portable relative paths")


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
            raise PackConfigurationError("PACK_API_VERSION", "pack apiVersion must be dryv.dev/v1", path="$.apiVersion")
        _identifier("pack id", self.id)
        if not self.version or self.version.strip() != self.version:
            raise PackConfigurationError("PACK_VERSION", "pack version must be non-empty and trimmed")
        for label, values in (
            ("option", tuple(item.name for item in self.options)),
            ("binding", tuple(item.name for item in self.bindings)),
            ("selection", tuple(item.key for item in self.selections)),
        ):
            if len(values) != len(set(values)):
                raise PackConfigurationError("PACK_DUPLICATE_ID", f"pack {label} names must be unique")
        selection_keys = {item.key for item in self.selections}
        binding_keys = {item.name for item in self.bindings}
        for selection in self.selections:
            for _, target in selection.imports:
                if target not in selection_keys:
                    raise PackConfigurationError("PACK_MISSING_SELECTION", f"selection {selection.key!r} imports unknown selection {target!r}")
            for target in selection.exports:
                if target not in selection_keys:
                    raise PackConfigurationError("PACK_MISSING_SELECTION", f"selection {selection.key!r} exports unknown selection {target!r}")
            for binding in selection.bindings:
                if binding not in binding_keys:
                    raise PackConfigurationError("PACK_MISSING_BINDING", f"selection {selection.key!r} uses unknown binding {binding!r}")

    def selection(self, key: str) -> SelectionConfig | None:
        return next((item for item in self.selections if item.key == key), None)

    def resolve_options(self, authored: FrozenObject) -> FrozenObject:
        definitions = {item.name: item for item in self.options}
        provided = dict(authored)
        unknown = sorted(set(provided) - set(definitions))
        if unknown:
            raise PackConfigurationError("PACK_UNKNOWN_OPTION", f"unknown pack option {unknown[0]!r}")
        resolved: list[tuple[str, FrozenValue]] = []
        for name in sorted(definitions):
            definition = definitions[name]
            value = provided.get(name, definition.default)
            if name not in provided and definition.required and definition.default is None:
                raise PackConfigurationError("PACK_REQUIRED_OPTION", f"required pack option {name!r} is missing")
            definition.validate(value)
            resolved.append((name, value))
        return tuple(resolved)

    def validate_bindings(self, authored: FrozenObject) -> None:
        definitions = {item.name: item for item in self.bindings}
        provided = set(dict(authored))
        unknown = sorted(provided - set(definitions))
        if unknown:
            raise PackConfigurationError("PACK_UNKNOWN_BINDING", f"unknown pack binding {unknown[0]!r}")
        missing = sorted(name for name, item in definitions.items() if item.required and name not in provided)
        if missing:
            raise PackConfigurationError("PACK_REQUIRED_BINDING", f"required pack binding {missing[0]!r} is missing")


@dataclass(frozen=True, slots=True)
class NormalizedPack:
    manifest: PackManifest
    templates: tuple[PackTemplateResource, ...]

    def __post_init__(self) -> None:
        resource_ids = tuple(item.resource_id for item in self.templates)
        if len(resource_ids) != len(set(resource_ids)):
            raise PackConfigurationError("PACK_DUPLICATE_RESOURCE", "template resource ids must be unique")
        selection_keys = {item.key for item in self.manifest.selections}
        for template in self.templates:
            if template.selection_key is not None and template.selection_key not in selection_keys:
                raise PackConfigurationError("PACK_MISSING_SELECTION", f"template references unknown selection {template.selection_key!r}")


def _identifier(label: str, value: str) -> None:
    if not value or value.strip() != value or any(character.isspace() for character in value):
        raise PackConfigurationError("PACK_IDENTIFIER", f"{label} must be a non-empty identifier")


__all__ = [
    "BindingDefinition",
    "FrozenObject",
    "FrozenValue",
    "NormalizedPack",
    "OptionDefinition",
    "PackConfigurationError",
    "PackManifest",
    "PackTemplateResource",
    "SelectionConfig",
]
