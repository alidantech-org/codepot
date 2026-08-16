from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum
from threading import Lock

from .protocol import (
    CancelRender,
    RenderClientTransport,
    RenderRequest,
    RendererHello,
    RenderStreamMessage,
    ValidateTemplateRequest,
    ValidateTemplateResult,
)


class RendererConnectionState(StrEnum):
    READY = "ready"
    CLOSED = "closed"


class RendererConnection:
    """One established Render Client plus bounded advertised capacity."""

    def __init__(
        self,
        connection_id: str,
        hello: RendererHello,
        transport: RenderClientTransport,
    ) -> None:
        if not connection_id or connection_id.strip() != connection_id:
            raise ValueError("renderer connection id must be non-empty and trimmed")
        self.connection_id = connection_id
        self.hello = hello
        self.transport = transport
        self._state = RendererConnectionState.READY
        self._active = 0
        self._lock = Lock()

    @property
    def state(self) -> RendererConnectionState:
        with self._lock:
            return self._state

    @property
    def active(self) -> int:
        with self._lock:
            return self._active

    @property
    def available(self) -> int:
        with self._lock:
            if self._state is RendererConnectionState.CLOSED:
                return 0
            return self.hello.max_concurrency - self._active

    def supports(self, capability: str) -> bool:
        return capability in self.hello.capabilities and self.state is RendererConnectionState.READY

    def reserve(self) -> bool:
        with self._lock:
            if self._state is RendererConnectionState.CLOSED:
                return False
            if self._active >= self.hello.max_concurrency:
                return False
            self._active += 1
            return True

    def release(self) -> None:
        with self._lock:
            if self._active < 1:
                raise RuntimeError("renderer connection has no reserved work")
            self._active -= 1

    def validate(self, request: ValidateTemplateRequest) -> ValidateTemplateResult:
        if not self.supports(request.capability):
            raise RuntimeError(f"renderer connection does not support {request.capability!r}")
        return self.transport.validate(request)

    def render(self, request: RenderRequest) -> Iterable[RenderStreamMessage]:
        if not self.supports(request.capability):
            raise RuntimeError(f"renderer connection does not support {request.capability!r}")
        return self.transport.render(request)

    def cancel(self, job_id: str) -> None:
        if self.state is RendererConnectionState.READY:
            self.transport.cancel(CancelRender(job_id))

    def close(self) -> None:
        with self._lock:
            if self._state is RendererConnectionState.CLOSED:
                return
            self._state = RendererConnectionState.CLOSED
        self.transport.close()


__all__ = ["RendererConnection", "RendererConnectionState"]
