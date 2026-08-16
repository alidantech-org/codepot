from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol, TypeAlias

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]

RENDER_PROTOCOL_VERSION = "dryv.render/v1"


@dataclass(frozen=True, slots=True)
class RendererHello:
    protocol: str
    renderer_id: str
    renderer_version: str
    fingerprint: str
    capabilities: tuple[str, ...]
    max_concurrency: int

    def __post_init__(self) -> None:
        if self.protocol != RENDER_PROTOCOL_VERSION:
            raise ValueError(f"renderer protocol must be {RENDER_PROTOCOL_VERSION!r}")
        if not self.renderer_id or not self.renderer_version or not self.fingerprint:
            raise ValueError("renderer identity, version and fingerprint are required")
        if tuple(sorted(set(self.capabilities))) != self.capabilities or not self.capabilities:
            raise ValueError("renderer capabilities must be sorted, unique and non-empty")
        if self.max_concurrency < 1:
            raise ValueError("renderer max_concurrency must be positive")


@dataclass(frozen=True, slots=True)
class TemplatePayload:
    resource_id: str
    media_type: str
    content_hash: str
    content: bytes


@dataclass(frozen=True, slots=True)
class ContextContractPayload:
    version: int
    paths: tuple[str, ...]
    hash: str


@dataclass(frozen=True, slots=True)
class ContextPayload:
    version: int
    value: JsonObject
    hash: str
    contract: ContextContractPayload


@dataclass(frozen=True, slots=True)
class PlannedOutputPayload:
    artifact_id: str
    path: str


@dataclass(frozen=True, slots=True)
class RendererDiagnostic:
    code: str
    message: str
    path: str | None = None
    line: int | None = None
    column: int | None = None


@dataclass(frozen=True, slots=True)
class ValidateTemplateRequest:
    validation_id: str
    capability: str
    template: TemplatePayload
    context_contract: ContextContractPayload


@dataclass(frozen=True, slots=True)
class ValidateTemplateResult:
    validation_id: str
    valid: bool
    diagnostics: tuple[RendererDiagnostic, ...] = ()


@dataclass(frozen=True, slots=True)
class RenderRequest:
    job_id: str
    capability: str
    template: TemplatePayload
    context: ContextPayload
    output: PlannedOutputPayload
    options: JsonObject


@dataclass(frozen=True, slots=True)
class ArtifactBegin:
    job_id: str
    artifact_id: str
    path: str
    media_type: str = "application/octet-stream"
    size: int | None = None


@dataclass(frozen=True, slots=True)
class ArtifactChunk:
    job_id: str
    artifact_id: str
    offset: int
    content: bytes


@dataclass(frozen=True, slots=True)
class ArtifactEnd:
    job_id: str
    artifact_id: str
    size: int
    content_hash: str


@dataclass(frozen=True, slots=True)
class RenderComplete:
    job_id: str


@dataclass(frozen=True, slots=True)
class RenderFailed:
    job_id: str
    diagnostics: tuple[RendererDiagnostic, ...]


@dataclass(frozen=True, slots=True)
class CancelRender:
    job_id: str


RenderStreamMessage: TypeAlias = ArtifactBegin | ArtifactChunk | ArtifactEnd | RenderComplete | RenderFailed


class RenderClientTransport(Protocol):
    def validate(self, request: ValidateTemplateRequest) -> ValidateTemplateResult: ...

    def render(self, request: RenderRequest) -> Iterable[RenderStreamMessage]: ...

    def cancel(self, request: CancelRender) -> None: ...

    def close(self) -> None: ...


__all__ = [
    "ArtifactBegin",
    "ArtifactChunk",
    "ArtifactEnd",
    "CancelRender",
    "ContextContractPayload",
    "ContextPayload",
    "JsonObject",
    "JsonValue",
    "PlannedOutputPayload",
    "RENDER_PROTOCOL_VERSION",
    "RenderClientTransport",
    "RenderComplete",
    "RenderFailed",
    "RenderRequest",
    "RendererDiagnostic",
    "RendererHello",
    "RenderStreamMessage",
    "TemplatePayload",
    "ValidateTemplateRequest",
    "ValidateTemplateResult",
]
