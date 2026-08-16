from __future__ import annotations

import base64
import json
from collections.abc import Iterable
from queue import Full, Queue
from threading import Lock, Thread
from typing import Any

from websockets.sync.client import connect

from dryv_api.renderers import (
    ArtifactBegin,
    ArtifactChunk,
    ArtifactEnd,
    CancelRender,
    ContextContractPayload,
    ContextPayload,
    PlannedOutputPayload,
    RENDER_PROTOCOL_VERSION,
    RenderComplete,
    RenderFailed,
    RenderRequest,
    RendererConnection,
    RendererDiagnostic,
    RendererHello,
    TemplatePayload,
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

_STOP = object()


class JinjaRenderClient:
    def __init__(self, *, max_concurrency: int = 1, chunk_bytes: int = 64 * 1024) -> None:
        if max_concurrency < 1 or chunk_bytes < 1:
            raise ValueError("renderer limits must be positive")
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

    def connection(self, connection_id: str = "local-jinja") -> RendererConnection:
        self._require_open()
        return RendererConnection(connection_id, self.hello, self)

    def serve(self, api_url: str, *, connection_id: str) -> None:
        self._require_open()
        outgoing: Queue[dict[str, object] | object] = Queue(maxsize=64)
        active: dict[str, Thread] = {}
        with connect(api_url, max_size=16 * 1024 * 1024, open_timeout=10.0) as socket:
            socket.send(json.dumps(_hello_document(connection_id, self.hello), sort_keys=True))

            def send_loop() -> None:
                while True:
                    document = outgoing.get()
                    if document is _STOP:
                        return
                    socket.send(json.dumps(document, sort_keys=True))

            sender = Thread(
                target=send_loop,
                name=f"dryv-jinja-send-{connection_id}",
                daemon=True,
            )
            sender.start()
            try:
                for raw in socket:
                    if not isinstance(raw, str):
                        raise RuntimeError("renderer WebSocket requires JSON text frames")
                    root = _object(json.loads(raw))
                    message_type = _string(root.get("type"), "type")
                    _discard_finished(active)
                    if message_type == "template.validate":
                        outgoing.put(_validation_document(self.validate(_decode_validate(root))))
                    elif message_type == "render.request":
                        request = _decode_render(root)
                        if request.job_id in active:
                            raise RuntimeError(f"renderer received duplicate render job {request.job_id!r}")
                        if len(active) >= self.max_concurrency:
                            raise RuntimeError("renderer received concurrent work beyond advertised capacity")
                        thread = Thread(
                            target=self._render_to_queue,
                            args=(request, outgoing),
                            name=f"dryv-jinja-render-{request.job_id}",
                            daemon=True,
                        )
                        active[request.job_id] = thread
                        thread.start()
                    elif message_type == "render.cancel":
                        self.cancel(CancelRender(_string(root.get("jobId"), "jobId")))
                    else:
                        raise RuntimeError(f"unknown renderer request {message_type!r}")
            finally:
                self.close()
                for thread in tuple(active.values()):
                    thread.join(timeout=2.0)
                try:
                    outgoing.put_nowait(_STOP)
                except Full:
                    pass
                sender.join(timeout=2.0)

    def _render_to_queue(
        self,
        request: RenderRequest,
        outgoing: Queue[dict[str, object] | object],
    ) -> None:
        for message in self.render(request):
            outgoing.put(_render_document(message))

    def _is_cancelled(self, job_id: str) -> bool:
        with self._lock:
            return self._closed or job_id in self._cancelled

    def _require_open(self) -> None:
        with self._lock:
            if self._closed:
                raise RuntimeError("Jinja Render Client is closed")


def _discard_finished(active: dict[str, Thread]) -> None:
    for job_id, thread in tuple(active.items()):
        if not thread.is_alive():
            active.pop(job_id, None)


def _hello_document(connection_id: str, hello: RendererHello) -> dict[str, object]:
    return {
        "type": "renderer.hello",
        "connectionId": connection_id,
        "protocol": hello.protocol,
        "rendererId": hello.renderer_id,
        "rendererVersion": hello.renderer_version,
        "fingerprint": hello.fingerprint,
        "capabilities": list(hello.capabilities),
        "maxConcurrency": hello.max_concurrency,
    }


def _decode_validate(root: dict[str, Any]) -> ValidateTemplateRequest:
    return ValidateTemplateRequest(
        _string(root.get("validationId"), "validationId"),
        _string(root.get("capability"), "capability"),
        _template(_object(root.get("template"))),
        _contract(_object(root.get("contextContract"))),
    )


def _decode_render(root: dict[str, Any]) -> RenderRequest:
    context_raw = _object(root.get("context"))
    output = _object(root.get("output"))
    value = context_raw.get("value")
    options = root.get("options", {})
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise RuntimeError("render context value must be an object")
    if not isinstance(options, dict) or not all(isinstance(key, str) for key in options):
        raise RuntimeError("render options must be an object")
    return RenderRequest(
        _string(root.get("jobId"), "jobId"),
        _string(root.get("capability"), "capability"),
        _template(_object(root.get("template"))),
        ContextPayload(
            _int(context_raw.get("version"), "context.version"),
            dict(value),
            _string(context_raw.get("hash"), "context.hash"),
            _contract(_object(context_raw.get("contract"))),
        ),
        PlannedOutputPayload(
            _string(output.get("artifactId"), "output.artifactId"),
            _string(output.get("path"), "output.path"),
        ),
        dict(options),
    )


def _template(value: dict[str, Any]) -> TemplatePayload:
    try:
        content = base64.b64decode(
            _string(value.get("contentBase64"), "contentBase64"), validate=True
        )
    except Exception as exc:
        raise RuntimeError("template contentBase64 is invalid") from exc
    return TemplatePayload(
        _string(value.get("resourceId"), "resourceId"),
        _string(value.get("mediaType"), "mediaType"),
        _string(value.get("contentHash"), "contentHash"),
        content,
    )


def _contract(value: dict[str, Any]) -> ContextContractPayload:
    paths = value.get("paths")
    if not isinstance(paths, list) or not all(isinstance(item, str) for item in paths):
        raise RuntimeError("context contract paths must be an array of strings")
    return ContextContractPayload(
        _int(value.get("version"), "contextContract.version"),
        tuple(paths),
        _string(value.get("hash"), "contextContract.hash"),
    )


def _validation_document(value: ValidateTemplateResult) -> dict[str, object]:
    return {
        "type": "template.validation",
        "validationId": value.validation_id,
        "valid": value.valid,
        "diagnostics": [_diagnostic_document(item) for item in value.diagnostics],
    }


def _render_document(value: RenderStreamMessage) -> dict[str, object]:
    if isinstance(value, ArtifactBegin):
        return {
            "type": "artifact.begin",
            "jobId": value.job_id,
            "artifactId": value.artifact_id,
            "path": value.path,
            "mediaType": value.media_type,
            "size": value.size,
        }
    if isinstance(value, ArtifactChunk):
        return {
            "type": "artifact.chunk",
            "jobId": value.job_id,
            "artifactId": value.artifact_id,
            "offset": value.offset,
            "contentBase64": base64.b64encode(value.content).decode("ascii"),
        }
    if isinstance(value, ArtifactEnd):
        return {
            "type": "artifact.end",
            "jobId": value.job_id,
            "artifactId": value.artifact_id,
            "size": value.size,
            "contentHash": value.content_hash,
        }
    if isinstance(value, RenderComplete):
        return {"type": "render.complete", "jobId": value.job_id}
    if isinstance(value, RenderFailed):
        return {
            "type": "render.failed",
            "jobId": value.job_id,
            "diagnostics": [_diagnostic_document(item) for item in value.diagnostics],
        }
    raise TypeError(f"unsupported render message {type(value).__name__}")


def _diagnostic_document(value: RendererDiagnostic) -> dict[str, object]:
    return {
        "code": value.code,
        "message": value.message,
        "path": value.path,
        "line": value.line,
        "column": value.column,
    }


def _object(value: object) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise RuntimeError("renderer request must be a JSON object")
    return dict(value)


def _string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise RuntimeError(f"{name} must be a non-empty string")
    return value


def _int(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise RuntimeError(f"{name} must be an integer")
    return value


__all__ = ["JinjaRenderClient"]
