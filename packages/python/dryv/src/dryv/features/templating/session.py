from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Mapping, Protocol, TypeAlias

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]

RENDER_PROTOCOL_VERSION = 1


class TemplatingError(ValueError):
    def __init__(self, code: str, message: str, *, job_id: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.job_id = job_id


@dataclass(frozen=True, slots=True)
class RendererHello:
    renderer_id: str
    renderer_version: str
    capabilities: tuple[str, ...]
    protocol_versions: tuple[int, ...]
    context_versions: tuple[int, ...]
    template_media_types: tuple[str, ...]
    fingerprint: str
    max_concurrency: int = 1
    deterministic: bool = True

    def __post_init__(self) -> None:
        if not self.renderer_id or not self.renderer_version or not self.fingerprint:
            raise ValueError("renderer hello requires identity, version and fingerprint")
        if self.max_concurrency < 1:
            raise ValueError("renderer max_concurrency must be positive")
        for values in (self.capabilities, self.protocol_versions, self.context_versions, self.template_media_types):
            if len(values) != len(set(values)):
                raise ValueError("renderer capability collections must be unique")


@dataclass(frozen=True, slots=True)
class PlannedOutput:
    id: str
    path: str

    def __post_init__(self) -> None:
        if not self.id or not self.path:
            raise ValueError("planned render outputs require id and path")


@dataclass(frozen=True, slots=True)
class RenderRequest:
    protocol_version: int
    context_version: int
    job_id: str
    required_capability: str
    template_resource_id: str
    template_media_type: str
    template_content: bytes
    template_hash: str
    context: Mapping[str, JsonValue]
    context_hash: str
    outputs: tuple[PlannedOutput, ...]
    options: tuple[tuple[str, JsonValue], ...] = ()

    def __post_init__(self) -> None:
        if self.protocol_version < 1 or self.context_version < 1:
            raise ValueError("render protocol and context versions must be positive")
        for label, value in (
            ("job id", self.job_id),
            ("renderer capability", self.required_capability),
            ("template resource id", self.template_resource_id),
            ("template media type", self.template_media_type),
            ("template hash", self.template_hash),
            ("context hash", self.context_hash),
        ):
            if not value or value.strip() != value:
                raise ValueError(f"render request {label} must be non-empty and trimmed")
        output_ids = tuple(item.id for item in self.outputs)
        if not output_ids or len(output_ids) != len(set(output_ids)):
            raise ValueError("render requests require unique planned output ids")
        option_names = tuple(name for name, _ in self.options)
        if tuple(sorted(option_names)) != option_names or len(option_names) != len(set(option_names)):
            raise ValueError("render options must be sorted by unique name")
        _validate_json(dict(self.context), "context")
        _validate_json({name: value for name, value in self.options}, "options")


@dataclass(frozen=True, slots=True)
class RenderDiagnostic:
    code: str
    message: str
    severity: str = "error"


@dataclass(frozen=True, slots=True)
class RenderedOutput:
    id: str
    content: bytes
    content_hash: str


@dataclass(frozen=True, slots=True)
class RenderResult:
    job_id: str
    renderer_fingerprint: str
    outputs: tuple[RenderedOutput, ...]
    diagnostics: tuple[RenderDiagnostic, ...] = ()
    cancelled: bool = False


class RenderSession(Protocol):
    def hello(self) -> RendererHello: ...
    def render(self, request: RenderRequest) -> RenderResult: ...
    def cancel(self, job_id: str) -> None: ...


@dataclass(frozen=True, slots=True)
class ValidatedRender:
    hello: RendererHello
    outputs: tuple[RenderedOutput, ...]
    diagnostics: tuple[RenderDiagnostic, ...]


class TemplatingFeature:
    def render(
        self,
        session: RenderSession,
        request: RenderRequest,
        *,
        content_hash: Callable[[bytes], str],
        is_cancelled: Callable[[], bool] | None = None,
    ) -> ValidatedRender:
        hello = session.hello()
        self._validate_hello(hello, request)
        if is_cancelled is not None and is_cancelled():
            session.cancel(request.job_id)
            raise TemplatingError("RENDER_CANCELLED", "render job was cancelled before submission", job_id=request.job_id)

        result = session.render(request)
        if is_cancelled is not None and is_cancelled():
            session.cancel(request.job_id)
            raise TemplatingError("RENDER_CANCELLED", "render job was cancelled", job_id=request.job_id)
        if result.job_id != request.job_id:
            raise TemplatingError("RENDER_JOB_MISMATCH", "renderer returned a result for a different job", job_id=request.job_id)
        if result.cancelled:
            raise TemplatingError("RENDER_CANCELLED", "renderer cancelled the render job", job_id=request.job_id)
        if result.renderer_fingerprint != hello.fingerprint:
            raise TemplatingError("RENDER_FINGERPRINT_MISMATCH", "renderer fingerprint changed during the job", job_id=request.job_id)

        allowed = {item.id for item in request.outputs}
        returned_ids = tuple(item.id for item in result.outputs)
        if len(returned_ids) != len(set(returned_ids)):
            raise TemplatingError("RENDER_DUPLICATE_OUTPUT", "renderer returned duplicate logical output ids", job_id=request.job_id)
        unknown = tuple(sorted(set(returned_ids) - allowed))
        if unknown:
            raise TemplatingError("RENDER_UNKNOWN_OUTPUT", f"renderer returned unplanned output {unknown[0]!r}", job_id=request.job_id)
        missing = tuple(sorted(allowed - set(returned_ids)))
        if missing:
            raise TemplatingError("RENDER_MISSING_OUTPUT", f"renderer omitted planned output {missing[0]!r}", job_id=request.job_id)
        for output in result.outputs:
            if content_hash(output.content) != output.content_hash:
                raise TemplatingError("RENDER_CONTENT_HASH", f"invalid content hash for output {output.id!r}", job_id=request.job_id)
        return ValidatedRender(hello, tuple(sorted(result.outputs, key=lambda item: item.id)), result.diagnostics)

    @staticmethod
    def _validate_hello(hello: RendererHello, request: RenderRequest) -> None:
        if request.required_capability not in hello.capabilities:
            raise TemplatingError("RENDER_CAPABILITY_MISMATCH", f"renderer does not provide {request.required_capability!r}", job_id=request.job_id)
        if request.protocol_version not in hello.protocol_versions:
            raise TemplatingError("RENDER_PROTOCOL_MISMATCH", "renderer does not support requested protocol version", job_id=request.job_id)
        if request.context_version not in hello.context_versions:
            raise TemplatingError("RENDER_CONTEXT_MISMATCH", "renderer does not support requested context version", job_id=request.job_id)
        if request.template_media_type not in hello.template_media_types:
            raise TemplatingError("RENDER_TEMPLATE_MEDIA_TYPE", f"renderer does not support {request.template_media_type!r}", job_id=request.job_id)


def _validate_json(value: object, label: str) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"render {label} numbers must be finite")
        return
    if isinstance(value, list | tuple):
        for item in value:
            _validate_json(item, label)
        return
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError(f"render {label} object keys must be strings")
        for item in value.values():
            _validate_json(item, label)
        return
    raise ValueError(f"render {label} contains unsupported value {type(value).__name__}")


__all__ = [
    "RENDER_PROTOCOL_VERSION",
    "PlannedOutput",
    "RenderDiagnostic",
    "RenderedOutput",
    "RendererHello",
    "RenderRequest",
    "RenderResult",
    "RenderSession",
    "TemplatingError",
    "TemplatingFeature",
    "ValidatedRender",
]
