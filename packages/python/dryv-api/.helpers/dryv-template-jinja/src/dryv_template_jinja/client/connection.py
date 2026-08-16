from __future__ import annotations

from collections.abc import Iterable
from threading import Lock

from dryv_api.renderers import (
    CancelRender,
    RENDER_PROTOCOL_VERSION,
    RenderRequest,
    RendererConnection,
    RendererHello,
    ValidateTemplateRequest,
    ValidateTemplateResult,
)
from dryv_api.renderers.protocol import RenderStreamMessage

from dryv_template_jinja.renderer import (
    PACKAGE_VERSION,
    RENDERER_CAPABILITY,
    RENDERER_ID,
    render_template,
    renderer_fingerprint,
    validate_template,
)


class JinjaRenderClient:
    def __init__(self, *, max_concurrency: int = 1, chunk_bytes: int = 64 * 1024) -> None:
        if max_concurrency < 1:
            raise ValueError("max_concurrency must be positive")
        if chunk_bytes < 1:
            raise ValueError("chunk_bytes must be positive")
        self.max_concurrency = max_concurrency
        self.chunk_bytes = chunk_bytes
        self._cancelled: set[str] = set()
        self._closed = False
        self._lock = Lock()

    @property
    def hello(self) -> RendererHello:
        return RendererHello(
            RENDER_PROTOCOL_VERSION,
            RENDERER_ID,
            PACKAGE_VERSION,
            renderer_fingerprint(),
            (RENDERER_CAPABILITY,),
            self.max_concurrency,
        )

    def validate(self, request: ValidateTemplateRequest) -> ValidateTemplateResult:
        self._require_open()
        return validate_template(request)

    def render(self, request: RenderRequest) -> Iterable[RenderStreamMessage]:
        self._require_open()
        with self._lock:
            self._cancelled.discard(request.job_id)
        return render_template(
            request,
            cancelled=lambda: self._is_cancelled(request.job_id),
            chunk_bytes=self.chunk_bytes,
        )

    def cancel(self, request: CancelRender) -> None:
        with self._lock:
            self._cancelled.add(request.job_id)

    def close(self) -> None:
        with self._lock:
            self._closed = True
            self._cancelled.clear()

    def connection(self, connection_id: str = "local-jinja") -> RendererConnection:
        self._require_open()
        return RendererConnection(connection_id, self.hello, self)

    def _is_cancelled(self, job_id: str) -> bool:
        with self._lock:
            return self._closed or job_id in self._cancelled

    def _require_open(self) -> None:
        with self._lock:
            if self._closed:
                raise RuntimeError("Jinja Render Client is closed")


__all__ = ["JinjaRenderClient"]
