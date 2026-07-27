from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import TypeAlias

from codepotg.ir import FrozenObject, FrozenValue

ConfigScalar: TypeAlias = str | int | float | bool | None
_MAX_VALUE_DEPTH = 64
_MAX_VALUE_ITEMS = 100_000


@dataclass(slots=True)
class _FreezeState:
    active: set[int] = field(default_factory=set)
    items: int = 0


def freeze_value(value: object, *, path: str = "$") -> FrozenValue:
    return _freeze_value(value, path=path, depth=0, state=_FreezeState())


def _freeze_value(
    value: object,
    *,
    path: str,
    depth: int,
    state: _FreezeState,
) -> FrozenValue:
    state.items += 1
    if state.items > _MAX_VALUE_ITEMS:
        raise ValueError(f"{path}: configuration value exceeds {_MAX_VALUE_ITEMS} items")
    if depth > _MAX_VALUE_DEPTH:
        raise ValueError(f"{path}: configuration value exceeds depth {_MAX_VALUE_DEPTH}")
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path}: non-finite numbers are not supported")
        return value
    if isinstance(value, list | tuple | dict):
        identity = id(value)
        if identity in state.active:
            raise ValueError(f"{path}: recursive configuration values are not supported")
        state.active.add(identity)
        try:
            if isinstance(value, list | tuple):
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
                raise ValueError(f"{path}: mapping keys must be non-empty strings")
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
    raise ValueError(f"{path}: unsupported configuration value {type(value).__name__}")


def freeze_object(value: object, *, path: str = "$") -> FrozenObject:
    frozen = freeze_value(value, path=path)
    if not isinstance(frozen, tuple) or (
        frozen and not all(isinstance(item, tuple) and len(item) == 2 for item in frozen)
    ):
        raise ValueError(f"{path}: expected an object")
    return frozen  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class SourceConfig:
    name: str
    adapter: str
    file: str
    options: FrozenObject = ()

    def __post_init__(self) -> None:
        _require_id("source name", self.name)
        _require_id("source adapter", self.adapter)
        _require_safe_relative_path("source file", self.file)


@dataclass(frozen=True, slots=True)
class PackSource:
    local: str | None = None
    git: str | None = None
    ref: str | None = None
    path: str | None = None

    def __post_init__(self) -> None:
        if (self.local is None) == (self.git is None):
            raise ValueError("pack source requires exactly one local or git locator")
        if self.local is not None:
            _require_safe_relative_path("local pack source", self.local)
            if self.ref is not None or self.path is not None:
                raise ValueError("local pack sources cannot declare ref or path")
        else:
            if not self.git or self.git.strip() != self.git:
                raise ValueError("git pack sources require a non-empty git locator")
            if not self.ref or self.ref.strip() != self.ref:
                raise ValueError("git pack sources require a non-empty ref")
            if self.path is not None:
                _require_safe_relative_path("git pack subdirectory", self.path)


@dataclass(frozen=True, slots=True)
class PackInstanceConfig:
    name: str
    source: PackSource
    input: str | None
    output: str
    options: FrozenObject = ()
    bindings: FrozenObject = ()
    executables: FrozenObject = ()
    commands: FrozenObject = ()

    def __post_init__(self) -> None:
        _require_id("pack instance", self.name)
        if self.input is not None:
            _require_id("pack input", self.input)
        _require_safe_relative_path("pack output", self.output)


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    api_version: str
    name: str
    sources: tuple[SourceConfig, ...]
    packs: tuple[PackInstanceConfig, ...]
    executables: FrozenObject = ()
    security: FrozenObject = ()
    commands: FrozenObject = ()

    def __post_init__(self) -> None:
        if self.api_version != "codepotg.dev/v2":
            raise ValueError("project apiVersion must be codepotg.dev/v2")
        _require_id("project name", self.name)
        source_names = tuple(item.name for item in self.sources)
        pack_names = tuple(item.name for item in self.packs)
        if len(source_names) != len(set(source_names)):
            raise ValueError("project source names must be unique")
        if len(pack_names) != len(set(pack_names)):
            raise ValueError("project pack instance names must be unique")
        available = set(source_names)
        for pack in self.packs:
            if pack.input is not None and pack.input not in available:
                raise ValueError(
                    f"pack {pack.name!r} references unknown input {pack.input!r}"
                )


@dataclass(frozen=True, slots=True)
class OptionDefinition:
    name: str
    default: FrozenValue = None
    choices: tuple[FrozenValue, ...] = ()
    required: bool = False
    description: str | None = None

    def validate(self, value: FrozenValue) -> None:
        if self.choices and value not in self.choices:
            raise ValueError(
                f"option {self.name!r} must be one of {self.choices!r}"
            )


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
        if self.select is not None and (
            not self.select or self.select.strip() != self.select
        ):
            raise ValueError("selection selector must be a non-empty trimmed string")
        import_names = tuple(name for name, _ in self.imports)
        if tuple(sorted(import_names)) != import_names or len(import_names) != len(
            set(import_names)
        ):
            raise ValueError("selection imports must be sorted by unique local name")
        for label, values in (
            ("selection exports", self.exports),
            ("selection bindings", self.bindings),
        ):
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
        if self.api_version != "codepotg.dev/v2":
            raise ValueError("pack apiVersion must be codepotg.dev/v2")
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
        missing = sorted(
            name
            for name, definition in definitions.items()
            if definition.required and name not in provided
        )
        if missing:
            raise ValueError(f"required pack binding {missing[0]!r} is missing")


def _require_id(label: str, value: str) -> None:
    if not value or value.strip() != value or any(character.isspace() for character in value):
        raise ValueError(f"{label} must be a non-empty identifier")


def _require_safe_relative_path(label: str, value: str) -> None:
    if not value or "\\" in value or value.startswith("/"):
        raise ValueError(f"{label} must be a non-empty POSIX-relative path")
    path = PurePosixPath(value)
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"{label} cannot contain empty, dot, or traversal segments")


def _require_path_segment(label: str, value: str) -> None:
    if not value or "/" in value or "\\" in value or value in {".", ".."}:
        raise ValueError(f"{label} values must be path segments")
