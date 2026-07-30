from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, runtime_checkable

from dryv.diagnostics import Diagnostics
from dryv.plugins import PluginDescriptor
from dryv.versions import BehaviorVersion


class IdentifierRole(StrEnum):
    TYPE = "type"
    VALUE = "value"
    PROPERTY = "property"
    PARAMETER = "parameter"
    ENUM_MEMBER = "enum_member"
    NAMESPACE = "namespace"
    FILE_STEM = "file_stem"


@dataclass(frozen=True, slots=True)
class TargetDescriptor:
    id: str
    aliases: tuple[str, ...]
    extensions: tuple[str, ...]
    behavior_version: BehaviorVersion
    capabilities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("target descriptors require an id")
        for label, values in (
            ("target aliases", self.aliases),
            ("target extensions", self.extensions),
            ("target capabilities", self.capabilities),
        ):
            if tuple(sorted(set(values))) != values:
                raise ValueError(f"{label} must be sorted and unique")
        if any(not extension.startswith(".") for extension in self.extensions):
            raise ValueError("target extensions must start with a dot")


@dataclass(frozen=True, slots=True)
class IdentifierValidationRequest:
    value: str
    role: IdentifierRole


@dataclass(frozen=True, slots=True)
class OutputPathValidationRequest:
    path: str
    target_id: str


class ModulePathKind(StrEnum):
    RELATIVE = "relative"
    PACKAGE = "package"
    ALIAS = "alias"
    EXPLICIT = "explicit"


@dataclass(frozen=True, slots=True)
class ModulePathRequest:
    current_artifact: str
    provider_artifact: str | None = None
    explicit_module: str | None = None
    package_name: str | None = None
    project_root: str | None = None

    def __post_init__(self) -> None:
        sources = sum(
            value is not None
            for value in (self.provider_artifact, self.explicit_module, self.package_name)
        )
        if sources != 1:
            raise ValueError(
                "module path requests require exactly one provider artifact, explicit module, or package"
            )


@dataclass(frozen=True, slots=True)
class ModulePathFacts:
    kind: ModulePathKind
    specifier: str
    current_artifact: str
    provider_artifact: str | None = None
    relative_path: str | None = None
    package_path: str | None = None

    def __post_init__(self) -> None:
        if not self.specifier:
            raise ValueError("module path facts require a specifier")


@runtime_checkable
class TargetAdapter(Protocol):
    @property
    def plugin(self) -> PluginDescriptor: ...

    @property
    def targets(self) -> tuple[TargetDescriptor, ...]: ...

    def validate_identifier(self, request: IdentifierValidationRequest) -> Diagnostics: ...

    def validate_output_path(self, request: OutputPathValidationRequest) -> Diagnostics: ...

    def resolve_module_path(self, request: ModulePathRequest) -> ModulePathFacts: ...
