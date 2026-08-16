from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import PurePosixPath
from typing import TypeAlias

ConfigScalar: TypeAlias = str | int | float | bool | None
FrozenValue: TypeAlias = ConfigScalar | tuple["FrozenValue", ...] | tuple[tuple[str, "FrozenValue"], ...]
FrozenObject: TypeAlias = tuple[tuple[str, FrozenValue], ...]

_MAX_VALUE_DEPTH = 64
_MAX_VALUE_ITEMS = 100_000


class CacheMode(StrEnum):
    USE = "use"
    REFRESH = "refresh"
    OFF = "off"


@dataclass(slots=True)
class _FreezeState:
    active: set[int] = field(default_factory=set)
    items: int = 0


def freeze_value(value: object, *, path: str = "$") -> FrozenValue:
    return _freeze(value, path=path, depth=0, state=_FreezeState())


def freeze_object(value: object, *, path: str = "$") -> FrozenObject:
    frozen = freeze_value(value, path=path)
    if not isinstance(frozen, tuple) or (
        frozen and not all(isinstance(item, tuple) and len(item) == 2 for item in frozen)
    ):
        raise ValueError(f"{path}: expected an object")
    return frozen  # type: ignore[return-value]


def thaw_object(value: FrozenObject) -> dict[str, object]:
    return {key: _thaw(item) for key, item in value}


@dataclass(frozen=True, slots=True)
class PackSource:
    local: str | None = None
    git: str | None = None
    ref: str | None = None
    path: str | None = None
    resource: str | None = None

    def __post_init__(self) -> None:
        if sum(item is not None for item in (self.local, self.git, self.resource)) != 1:
            raise ValueError("pack source requires exactly one local, git, or resource locator")
        if self.local is not None:
            _relative_path("local pack source", self.local)
            if self.ref is not None or self.path is not None:
                raise ValueError("local pack sources cannot declare ref or path")
        elif self.git is not None:
            if not self.git or self.git.strip() != self.git:
                raise ValueError("git pack source must be non-empty and trimmed")
            if not self.ref or self.ref.strip() != self.ref:
                raise ValueError("git pack source requires an explicit ref")
            if self.path is not None:
                _relative_path("git pack path", self.path)
        else:
            assert self.resource is not None
            _resource_id("pack resource", self.resource)
            if self.ref is not None or self.path is not None:
                raise ValueError("resource pack sources cannot declare ref or path")


@dataclass(frozen=True, slots=True)
class PackInstanceConfig:
    name: str
    source: PackSource
    output: str
    options: FrozenObject = ()
    bindings: FrozenObject = ()

    def __post_init__(self) -> None:
        _identifier("pack instance", self.name)
        _relative_path("pack output", self.output)


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    api_version: str
    name: str
    packs: tuple[PackInstanceConfig, ...]
    resources: tuple[str, ...] = ()
    cache_mode: CacheMode = CacheMode.USE

    def __post_init__(self) -> None:
        if self.api_version != "dryv.dev/v1":
            raise ValueError("project apiVersion must be dryv.dev/v1")
        _identifier("project name", self.name)
        names = tuple(item.name for item in self.packs)
        if len(names) != len(set(names)):
            raise ValueError("project pack instance names must be unique")
        if tuple(sorted(set(self.resources))) != self.resources:
            raise ValueError("project resources must be sorted and unique")
        for resource in self.resources:
            _resource_id("project resource", resource)

    def pack(self, name: str) -> PackInstanceConfig | None:
        return next((item for item in self.packs if item.name == name), None)


def _freeze(value: object, *, path: str, depth: int, state: _FreezeState) -> FrozenValue:
    state.items += 1
    if state.items > _MAX_VALUE_ITEMS:
        raise ValueError(f"{path}: configuration exceeds {_MAX_VALUE_ITEMS} values")
    if depth > _MAX_VALUE_DEPTH:
        raise ValueError(f"{path}: configuration exceeds depth {_MAX_VALUE_DEPTH}")
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path}: non-finite numbers are not supported")
        return value
    if isinstance(value, (list, tuple, dict)):
        identity = id(value)
        if identity in state.active:
            raise ValueError(f"{path}: recursive values are not supported")
        state.active.add(identity)
        try:
            if isinstance(value, (list, tuple)):
                return tuple(
                    _freeze(item, path=f"{path}[{index}]", depth=depth + 1, state=state)
                    for index, item in enumerate(value)
                )
            if not all(isinstance(key, str) and key for key in value):
                raise ValueError(f"{path}: object keys must be non-empty strings")
            return tuple(
                (key, _freeze(value[key], path=f"{path}.{key}", depth=depth + 1, state=state))
                for key in sorted(value)
            )
        finally:
            state.active.remove(identity)
    raise ValueError(f"{path}: unsupported configuration value {type(value).__name__}")


def _thaw(value: FrozenValue) -> object:
    if not isinstance(value, tuple):
        return value
    if value and all(isinstance(item, tuple) and len(item) == 2 for item in value):
        return {key: _thaw(item) for key, item in value}  # type: ignore[misc]
    return [_thaw(item) for item in value]


def _identifier(label: str, value: str) -> None:
    if not value or value.strip() != value or any(character.isspace() for character in value):
        raise ValueError(f"{label} must be a non-empty identifier")


def _relative_path(label: str, value: str) -> None:
    if not value or value.startswith("/") or "\\" in value:
        raise ValueError(f"{label} must be a POSIX-relative path")
    path = PurePosixPath(value)
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"{label} cannot contain empty, dot, or traversal segments")


def _resource_id(label: str, value: str) -> None:
    if not value.startswith("resource://") or value.strip() != value or "\\" in value:
        raise ValueError(f"{label} must use resource://")
    parts = value.removeprefix("resource://").split("/")
    if len(parts) < 2 or any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"{label} contains an invalid resource path")


__all__ = [
    "CacheMode",
    "FrozenObject",
    "FrozenValue",
    "PackInstanceConfig",
    "PackSource",
    "ProjectConfig",
    "freeze_object",
    "freeze_value",
    "thaw_object",
]
