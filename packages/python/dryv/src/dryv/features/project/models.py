from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import PurePosixPath
from typing import TypeAlias

from dryv.ir import FrozenObject, FrozenValue

ConfigScalar: TypeAlias = str | int | float | bool | None
_MAX_VALUE_DEPTH = 64
_MAX_VALUE_ITEMS = 100_000


class CacheMode(StrEnum):
    USE = "use"
    REFRESH = "refresh"
    OFF = "off"


class BuildMode(StrEnum):
    RENDER = "render"
    PLAN = "plan"
    STREAM = "stream"


@dataclass(slots=True)
class _FreezeState:
    active: set[int] = field(default_factory=set)
    items: int = 0


def freeze_value(value: object, *, path: str = "$") -> FrozenValue:
    return _freeze_value(value, path=path, depth=0, state=_FreezeState())


def _freeze_value(value: object, *, path: str, depth: int, state: _FreezeState) -> FrozenValue:
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
                return tuple(_freeze_value(item, path=f"{path}[{index}]", depth=depth + 1, state=state) for index, item in enumerate(value))
            if not all(isinstance(key, str) and key for key in value):
                raise ValueError(f"{path}: mapping keys must be non-empty strings")
            return tuple((key, _freeze_value(value[key], path=f"{path}.{key}", depth=depth + 1, state=state)) for key in sorted(value))
        finally:
            state.active.remove(identity)
    raise ValueError(f"{path}: unsupported configuration value {type(value).__name__}")


def freeze_object(value: object, *, path: str = "$") -> FrozenObject:
    frozen = freeze_value(value, path=path)
    if not isinstance(frozen, tuple) or (frozen and not all(isinstance(item, tuple) and len(item) == 2 for item in frozen)):
        raise ValueError(f"{path}: expected an object")
    return frozen  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class SourceConfig:
    name: str
    adapter: str | None = None
    file: str | None = None
    options: FrozenObject = ()
    resource: str | None = None
    author: str | None = None
    resources: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_id("source name", self.name)
        legacy = self.adapter is not None or self.file is not None
        ir_resource = self.resource is not None
        author_backend = self.author is not None
        if sum((legacy, ir_resource, author_backend)) != 1:
            raise ValueError("source requires exactly one IR resource, Author Backend, or legacy adapter source")
        if legacy:
            if self.adapter is None or self.file is None:
                raise ValueError("legacy source requires both adapter and file")
            _require_id("source adapter", self.adapter)
            _require_safe_relative_path("source file", self.file)
            if self.resources:
                raise ValueError("legacy source cannot declare logical resources")
        elif ir_resource:
            assert self.resource is not None
            _require_resource_id("IR source resource", self.resource)
            if self.resources:
                raise ValueError("IR resource source cannot declare author resources")
        else:
            assert self.author is not None
            _require_id("author backend", self.author)
            for item in self.resources:
                _require_resource_id("author resource", item)
            if tuple(sorted(set(self.resources))) != self.resources:
                raise ValueError("author resources must be sorted and unique")

    @property
    def kind(self) -> str:
        if self.resource is not None:
            return "ir"
        if self.author is not None:
            return "author"
        return "legacy"


@dataclass(frozen=True, slots=True)
class PackSource:
    local: str | None = None
    git: str | None = None
    ref: str | None = None
    path: str | None = None
    resource: str | None = None

    def __post_init__(self) -> None:
        selected = sum(item is not None for item in (self.local, self.git, self.resource))
        if selected != 1:
            raise ValueError("pack source requires exactly one local, git, or resource locator")
        if self.local is not None:
            _require_safe_relative_path("local pack source", self.local)
            if self.ref is not None or self.path is not None:
                raise ValueError("local pack sources cannot declare ref or path")
        elif self.git is not None:
            if not self.git or self.git.strip() != self.git:
                raise ValueError("git pack sources require a non-empty git locator")
            if not self.ref or self.ref.strip() != self.ref:
                raise ValueError("git pack sources require a non-empty ref")
            if self.path is not None:
                _require_safe_relative_path("git pack subdirectory", self.path)
        else:
            assert self.resource is not None
            _require_resource_id("pack resource", self.resource)
            if self.ref is not None or self.path is not None:
                raise ValueError("resource pack sources cannot declare ref or path")


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
    bindings: FrozenObject = ()
    resources: tuple[str, ...] = ()
    cache_mode: CacheMode = CacheMode.USE
    build_mode: BuildMode = BuildMode.RENDER
    renderers: FrozenObject = ()

    def __post_init__(self) -> None:
        if self.api_version != "dryv.dev/v1":
            raise ValueError("project apiVersion must be dryv.dev/v1")
        _require_id("project name", self.name)
        if not self.sources:
            raise ValueError("project requires at least one IR or author source")
        source_names = tuple(item.name for item in self.sources)
        pack_names = tuple(item.name for item in self.packs)
        if len(source_names) != len(set(source_names)):
            raise ValueError("project source names must be unique")
        if len(pack_names) != len(set(pack_names)):
            raise ValueError("project pack instance names must be unique")
        if tuple(sorted(set(self.resources))) != self.resources:
            raise ValueError("project resources must be sorted and unique")
        for resource in self.resources:
            _require_resource_id("project resource", resource)
        available = set(source_names)
        for pack in self.packs:
            if pack.input is not None and pack.input not in available:
                raise ValueError(f"pack {pack.name!r} references unknown input {pack.input!r}")


def _require_id(label: str, value: str) -> None:
    if not value or value.strip() != value or any(character.isspace() for character in value):
        raise ValueError(f"{label} must be a non-empty identifier")


def _require_safe_relative_path(label: str, value: str) -> None:
    if not value or "\\" in value or value.startswith("/"):
        raise ValueError(f"{label} must be a non-empty POSIX-relative path")
    path = PurePosixPath(value)
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"{label} cannot contain empty, dot, or traversal segments")


def _require_resource_id(label: str, value: str) -> None:
    if not value.startswith("resource://") or value.strip() != value or "\\" in value:
        raise ValueError(f"{label} must use a resource:// logical identifier")
    remainder = value.removeprefix("resource://")
    if not remainder or any(part in {"", ".", ".."} for part in remainder.split("/")):
        raise ValueError(f"{label} contains an invalid resource path")


__all__ = ["BuildMode", "CacheMode", "ConfigScalar", "PackInstanceConfig", "PackSource", "ProjectConfig", "SourceConfig", "freeze_object", "freeze_value"]
