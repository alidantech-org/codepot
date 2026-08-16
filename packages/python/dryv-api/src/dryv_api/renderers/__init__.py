"""External Render Client protocol, registry, preflight and scheduling."""

from .connection import RendererConnection, RendererConnectionState
from .preflight import (
    JobPreflight,
    PreflightCoordinator,
    PreflightKey,
    PreflightReport,
    TemplatePreflightError,
)
from .protocol import (
    RENDER_PROTOCOL_VERSION,
    ArtifactBegin,
    ArtifactChunk,
    ArtifactEnd,
    CancelRender,
    ContextContractPayload,
    ContextPayload,
    PlannedOutputPayload,
    RenderClientTransport,
    RenderComplete,
    RenderFailed,
    RendererDiagnostic,
    RendererHello,
    RenderRequest,
    TemplatePayload,
    ValidateTemplateRequest,
    ValidateTemplateResult,
)
from .registry import RendererRegistry
from .scheduler import RenderExecution, RenderExecutionError, RenderScheduler

__all__ = [
    "ArtifactBegin",
    "ArtifactChunk",
    "ArtifactEnd",
    "CancelRender",
    "ContextContractPayload",
    "ContextPayload",
    "JobPreflight",
    "PlannedOutputPayload",
    "PreflightCoordinator",
    "PreflightKey",
    "PreflightReport",
    "RENDER_PROTOCOL_VERSION",
    "RenderClientTransport",
    "RenderComplete",
    "RenderExecution",
    "RenderExecutionError",
    "RenderFailed",
    "RenderRequest",
    "RenderScheduler",
    "RendererConnection",
    "RendererConnectionState",
    "RendererDiagnostic",
    "RendererHello",
    "RendererRegistry",
    "TemplatePayload",
    "TemplatePreflightError",
    "ValidateTemplateRequest",
    "ValidateTemplateResult",
]
