from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable

from .core import BehaviorVersion, CancellationToken, Diagnostics
from .ir import Contract, FrozenObject
from .plugins import PluginDescriptor


@dataclass(frozen=True, slots=True)
class SourceAdapterRequest:
    source_id: str
    location: str | None = None
    content: str | bytes | None = None
    options: FrozenObject = ()

    def __post_init__(self) -> None:
        if not self.source_id:
            raise ValueError("source adapter requests require source_id")
        if self.location is None and self.content is None:
            raise ValueError("source adapter requests require location or in-memory content")
        if self.location is not None and self.content is not None:
            raise ValueError("source adapter requests accept location or content, not both")


@dataclass(frozen=True, slots=True)
class SourceAdapterResult:
    contract: Contract | None
    digest: str | None
    diagnostics: Diagnostics = Diagnostics()

    def __post_init__(self) -> None:
        if self.contract is not None and not self.digest:
            raise ValueError("successful source results require a stable digest")
        if self.contract is None and not self.diagnostics.has_errors:
            raise ValueError("missing source contract requires an error diagnostic")


class IdentifierRole(str, Enum):
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
        if tuple(sorted(set(self.aliases))) != self.aliases:
            raise ValueError("target aliases must be sorted and unique")
        if tuple(sorted(set(self.extensions))) != self.extensions:
            raise ValueError("target extensions must be sorted and unique")
        if tuple(sorted(set(self.capabilities))) != self.capabilities:
            raise ValueError("target capabilities must be sorted and unique")
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


class ModulePathKind(str, Enum):
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


@dataclass(frozen=True, slots=True)
class RenderRequest:
    template_id: str
    source: str
    context: tuple[tuple[str, object], ...] = ()
    partials: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.template_id:
            raise ValueError("render requests require template_id")
        if tuple(sorted(self.context, key=lambda item: item[0])) != self.context:
            raise ValueError("render context must be sorted by key")
        if tuple(sorted(self.partials, key=lambda item: item[0])) != self.partials:
            raise ValueError("render partials must be sorted by key")


@dataclass(frozen=True, slots=True)
class RenderResult:
    content: str | None
    diagnostics: Diagnostics = Diagnostics()

    def __post_init__(self) -> None:
        if self.content is None and not self.diagnostics.has_errors:
            raise ValueError("missing rendered content requires an error diagnostic")


@runtime_checkable
class SourceAdapter(Protocol):
    @property
    def plugin(self) -> PluginDescriptor: ...

    def normalize(
        self,
        request: SourceAdapterRequest,
        cancellation: CancellationToken,
    ) -> SourceAdapterResult: ...


@runtime_checkable
class TargetAdapter(Protocol):
    @property
    def plugin(self) -> PluginDescriptor: ...

    @property
    def targets(self) -> tuple[TargetDescriptor, ...]: ...

    def validate_identifier(self, request: IdentifierValidationRequest) -> Diagnostics: ...

    def validate_output_path(self, request: OutputPathValidationRequest) -> Diagnostics: ...

    def resolve_module_path(self, request: ModulePathRequest) -> ModulePathFacts: ...


@runtime_checkable
class TemplateEngine(Protocol):
    @property
    def plugin(self) -> PluginDescriptor: ...

    @property
    def suffixes(self) -> tuple[str, ...]: ...

    def render(
        self,
        request: RenderRequest,
        cancellation: CancellationToken,
    ) -> RenderResult: ...
