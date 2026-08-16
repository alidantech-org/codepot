from __future__ import annotations

import asyncio
import base64
from collections.abc import Iterable
from queue import Empty, Queue
from threading import Event, Lock
from typing import Any

from starlette.websockets import WebSocket, WebSocketDisconnect

from dryv_api.contracts import BuildStatus, DeliveryMode
from dryv_api.delivery import ArtifactData, ArtifactFinished, ArtifactStarted
from dryv_api.renderers import (
    ArtifactBegin,
    ArtifactChunk,
    ArtifactEnd,
    CancelRender,
    ContextContractPayload,
    RenderClientTransport,
    RenderComplete,
    RenderFailed,
    RendererConnection,
    RendererDiagnostic,
    RendererHello,
    RenderRequest,
    TemplatePayload,
    ValidateTemplateRequest,
    ValidateTemplateResult,
)
from dryv_api.renderers.protocol import RenderStreamMessage
from dryv_api.server import DryvApiServer

_TERMINAL = {BuildStatus.RENDER_COMPLETE, BuildStatus.CANCELLED, BuildStatus.FAILED}
_STOP = object()


async def build_events(websocket: WebSocket) -> None:
    server: DryvApiServer = websocket.app.state.dryv_server
    build_id = websocket.path_params["build_id"]
    try:
        session = server.build(build_id)
    except Exception:
        await websocket.close(code=4404)
        return
    await websocket.accept()
    after = 0
    stream_finished = False
    try:
        while True:
            for event in session.events(after_sequence=after):
                after = event.sequence
                await websocket.send_json(
                    {
                        "type": event.type.value,
                        "sequence": event.sequence,
                        "buildId": event.build_id,
                        "message": event.message,
                        "subject": event.subject,
                        "details": dict(event.details),
                        "runtimeStage": event.runtime_stage,
                    }
                )
            execution = server.execution(build_id)
            if (
                execution is not None
                and session.normalized.delivery is DeliveryMode.STREAM
                and not stream_finished
            ):
                item = await asyncio.to_thread(execution.stream.receive, timeout=0.05)
                if item is not None:
                    await websocket.send_json(_artifact_document(item))
                elif execution.done.is_set() and execution.stream.closed:
                    stream_finished = True
                    await websocket.send_json(
                        {"type": "artifact.stream.complete", "buildId": build_id}
                    )
            status = session.status
            if status in _TERMINAL:
                if session.normalized.delivery is DeliveryMode.BUNDLE:
                    handle = server.bundle(build_id)
                    if handle is not None and not handle.ready.is_set():
                        await asyncio.sleep(0.05)
                        continue
                if (
                    session.normalized.delivery is DeliveryMode.STREAM
                    and execution is not None
                    and not stream_finished
                ):
                    await asyncio.sleep(0.05)
                    continue
                return
            await asyncio.sleep(0.05)
    except WebSocketDisconnect:
        if session.normalized.delivery is DeliveryMode.STREAM:
            server.cancel_build(build_id)


async def renderer_connection(websocket: WebSocket) -> None:
    server: DryvApiServer = websocket.app.state.dryv_server
    await websocket.accept()
    transport: RemoteRendererTransport | None = None
    connection_id: str | None = None
    registered = False
    try:
        hello_document = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
        connection_id, hello = _decode_hello(hello_document)
        transport = RemoteRendererTransport()
        server.register_renderer(RendererConnection(connection_id, hello, transport))
        registered = True
        sender = asyncio.create_task(_renderer_sender(websocket, transport))
        receiver = asyncio.create_task(_renderer_receiver(websocket, transport))
        done, pending = await asyncio.wait(
            (sender, receiver), return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
        for task in done:
            error = task.exception()
            if error is not None and not isinstance(error, WebSocketDisconnect):
                raise error
    except WebSocketDisconnect:
        pass
    finally:
        if transport is not None:
            transport.close()
        if registered and connection_id is not None:
            server.unregister_renderer(connection_id, close=False)


class RemoteRendererTransport(RenderClientTransport):
    """Bridge synchronous renderer calls to one renderer WebSocket with bounded queues."""

    def __init__(self) -> None:
        self._outgoing: Queue[dict[str, object] | object] = Queue(maxsize=64)
        self._responses: dict[str, Queue[object]] = {}
        self._lock = Lock()
        self._closed = Event()

    def validate(self, request: ValidateTemplateRequest) -> ValidateTemplateResult:
        key = f"validate:{request.validation_id}"
        queue = self._open_response(key)
        self._send(_validate_document(request))
        try:
            result = queue.get()
            if isinstance(result, Exception):
                raise result
            if not isinstance(result, ValidateTemplateResult):
                raise RuntimeError("renderer returned an invalid template validation response")
            return result
        finally:
            self._close_response(key)

    def render(self, request: RenderRequest) -> Iterable[RenderStreamMessage]:
        key = f"render:{request.job_id}"
        queue = self._open_response(key)
        self._send(_render_document(request))

        def messages() -> Iterable[RenderStreamMessage]:
            try:
                while True:
                    item = queue.get()
                    if isinstance(item, Exception):
                        raise item
                    if not isinstance(
                        item,
                        (
                            ArtifactBegin,
                            ArtifactChunk,
                            ArtifactEnd,
                            RenderComplete,
                            RenderFailed,
                        ),
                    ):
                        raise RuntimeError("renderer returned an invalid render response")
                    yield item
                    if isinstance(item, (RenderComplete, RenderFailed)):
                        return
            finally:
                self._close_response(key)

        return messages()

    def cancel(self, request: CancelRender) -> None:
        if not self._closed.is_set():
            self._send({"type": "render.cancel", "jobId": request.job_id})

    def close(self) -> None:
        if self._closed.is_set():
            return
        self._closed.set()
        try:
            self._outgoing.put_nowait(_STOP)
        except Exception:
            pass
        with self._lock:
            queues = tuple(self._responses.values())
            self._responses.clear()
        error = RuntimeError("renderer WebSocket disconnected")
        for queue in queues:
            try:
                while True:
                    queue.get_nowait()
            except Empty:
                pass
            queue.put_nowait(error)

    def next_outgoing(self) -> dict[str, object] | None:
        value = self._outgoing.get()
        return None if value is _STOP else value  # type: ignore[return-value]

    def accept(self, document: object) -> None:
        root = _object(document)
        message_type = _string(root.get("type"), "type")
        if message_type == "template.validation":
            validation_id = _string(root.get("validationId"), "validationId")
            self._deliver(
                f"validate:{validation_id}",
                ValidateTemplateResult(
                    validation_id,
                    _bool(root.get("valid"), "valid"),
                    _diagnostics(root.get("diagnostics", [])),
                ),
            )
            return
        job_id = _string(root.get("jobId"), "jobId")
        if message_type == "artifact.begin":
            value: object = ArtifactBegin(
                job_id,
                _string(root.get("artifactId"), "artifactId"),
                _string(root.get("path"), "path"),
                _string(root.get("mediaType"), "mediaType"),
                _optional_int(root.get("size"), "size"),
            )
        elif message_type == "artifact.chunk":
            try:
                content = base64.b64decode(
                    _string(root.get("contentBase64"), "contentBase64"), validate=True
                )
            except Exception:
                self._deliver(
                    f"render:{job_id}",
                    RuntimeError("renderer artifact chunk is invalid base64"),
                )
                return
            value = ArtifactChunk(
                job_id,
                _string(root.get("artifactId"), "artifactId"),
                _int(root.get("offset"), "offset"),
                content,
            )
        elif message_type == "artifact.end":
            value = ArtifactEnd(
                job_id,
                _string(root.get("artifactId"), "artifactId"),
                _int(root.get("size"), "size"),
                _string(root.get("contentHash"), "contentHash"),
            )
        elif message_type == "render.complete":
            value = RenderComplete(job_id)
        elif message_type == "render.failed":
            value = RenderFailed(job_id, _diagnostics(root.get("diagnostics", [])))
        else:
            raise RuntimeError(f"unknown renderer WebSocket message {message_type!r}")
        self._deliver(f"render:{job_id}", value)

    def _send(self, document: dict[str, object]) -> None:
        if self._closed.is_set():
            raise RuntimeError("renderer WebSocket is closed")
        self._outgoing.put(document)

    def _open_response(self, key: str) -> Queue[object]:
        queue: Queue[object] = Queue(maxsize=64)
        with self._lock:
            if self._closed.is_set():
                raise RuntimeError("renderer WebSocket is closed")
            if key in self._responses:
                raise RuntimeError(f"duplicate renderer request {key!r}")
            self._responses[key] = queue
        return queue

    def _close_response(self, key: str) -> None:
        with self._lock:
            self._responses.pop(key, None)

    def _deliver(self, key: str, value: object) -> None:
        with self._lock:
            queue = self._responses.get(key)
        if queue is None:
            raise RuntimeError(f"renderer response has no active request {key!r}")
        queue.put(value)


async def _renderer_sender(
    websocket: WebSocket, transport: RemoteRendererTransport
) -> None:
    while True:
        document = await asyncio.to_thread(transport.next_outgoing)
        if document is None:
            return
        await websocket.send_json(document)


async def _renderer_receiver(
    websocket: WebSocket, transport: RemoteRendererTransport
) -> None:
    while True:
        document = await websocket.receive_json()
        await asyncio.to_thread(transport.accept, document)


def _decode_hello(value: object) -> tuple[str, RendererHello]:
    root = _object(value)
    if root.get("type") != "renderer.hello":
        raise RuntimeError("renderer WebSocket must begin with renderer.hello")
    connection_id = _string(root.get("connectionId"), "connectionId")
    capabilities_raw = root.get("capabilities")
    if not isinstance(capabilities_raw, list) or not all(
        isinstance(item, str) for item in capabilities_raw
    ):
        raise RuntimeError("renderer capabilities must be an array of strings")
    return connection_id, RendererHello(
        _string(root.get("protocol"), "protocol"),
        _string(root.get("rendererId"), "rendererId"),
        _string(root.get("rendererVersion"), "rendererVersion"),
        _string(root.get("fingerprint"), "fingerprint"),
        tuple(capabilities_raw),
        _int(root.get("maxConcurrency"), "maxConcurrency"),
    )


def _validate_document(request: ValidateTemplateRequest) -> dict[str, object]:
    return {
        "type": "template.validate",
        "validationId": request.validation_id,
        "capability": request.capability,
        "template": _template_document(request.template),
        "contextContract": _contract_document(request.context_contract),
    }


def _render_document(request: RenderRequest) -> dict[str, object]:
    return {
        "type": "render.request",
        "jobId": request.job_id,
        "capability": request.capability,
        "template": _template_document(request.template),
        "context": {
            "version": request.context.version,
            "value": request.context.value,
            "hash": request.context.hash,
            "contract": _contract_document(request.context.contract),
        },
        "output": {
            "artifactId": request.output.artifact_id,
            "path": request.output.path,
        },
        "options": request.options,
    }


def _template_document(value: TemplatePayload) -> dict[str, object]:
    return {
        "resourceId": value.resource_id,
        "mediaType": value.media_type,
        "contentHash": value.content_hash,
        "contentBase64": base64.b64encode(value.content).decode("ascii"),
    }


def _contract_document(value: ContextContractPayload) -> dict[str, object]:
    return {"version": value.version, "paths": list(value.paths), "hash": value.hash}


def _artifact_document(value: object) -> dict[str, object]:
    if isinstance(value, ArtifactStarted):
        return {
            "type": "artifact.begin",
            "jobId": value.job_id,
            "artifactId": value.artifact_id,
            "planIndex": value.plan_index,
            "path": value.path,
            "dependencies": list(value.dependencies),
            "mediaType": value.media_type,
            "size": value.size,
        }
    if isinstance(value, ArtifactData):
        return {
            "type": "artifact.chunk",
            "jobId": value.job_id,
            "artifactId": value.artifact_id,
            "planIndex": value.plan_index,
            "offset": value.offset,
            "contentBase64": base64.b64encode(value.content).decode("ascii"),
        }
    if isinstance(value, ArtifactFinished):
        return {
            "type": "artifact.end",
            "jobId": value.job_id,
            "artifactId": value.artifact_id,
            "planIndex": value.plan_index,
            "path": value.path,
            "size": value.size,
            "contentHash": value.content_hash,
        }
    raise TypeError(f"unsupported artifact event {type(value).__name__}")


def _diagnostics(value: object) -> tuple[RendererDiagnostic, ...]:
    if not isinstance(value, list):
        raise RuntimeError("renderer diagnostics must be an array")
    result: list[RendererDiagnostic] = []
    for raw in value:
        item = _object(raw)
        result.append(
            RendererDiagnostic(
                _string(item.get("code"), "code"),
                _string(item.get("message"), "message"),
                item.get("path") if isinstance(item.get("path"), str) else None,
                _optional_int(item.get("line"), "line"),
                _optional_int(item.get("column"), "column"),
            )
        )
    return tuple(result)


def _object(value: object) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise RuntimeError("renderer message must be a JSON object")
    return dict(value)


def _string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise RuntimeError(f"renderer message {name} must be a non-empty string")
    return value


def _bool(value: object, name: str) -> bool:
    if not isinstance(value, bool):
        raise RuntimeError(f"renderer message {name} must be a boolean")
    return value


def _int(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise RuntimeError(f"renderer message {name} must be an integer")
    return value


def _optional_int(value: object, name: str) -> int | None:
    if value is None:
        return None
    return _int(value, name)


__all__ = ["RemoteRendererTransport", "build_events", "renderer_connection"]
