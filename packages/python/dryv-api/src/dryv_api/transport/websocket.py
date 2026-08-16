from __future__ import annotations

import asyncio
import base64

from starlette.websockets import WebSocket, WebSocketDisconnect

from dryv_api.contracts import BuildStatus, DeliveryMode
from dryv_api.delivery import ArtifactData, ArtifactFinished, ArtifactStarted
from dryv_api.server import DryvApiServer

_TERMINAL = {BuildStatus.RENDER_COMPLETE, BuildStatus.CANCELLED, BuildStatus.FAILED}


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
            if execution is not None and session.normalized.delivery is DeliveryMode.STREAM and not stream_finished:
                item = await asyncio.to_thread(execution.stream.receive, timeout=0.05)
                if item is not None:
                    await websocket.send_json(_artifact_document(item))
                elif execution.done.is_set() and execution.stream.closed:
                    stream_finished = True
                    await websocket.send_json({"type": "artifact.stream.complete", "buildId": build_id})

            status = session.status
            if status in _TERMINAL:
                if session.normalized.delivery is DeliveryMode.BUNDLE:
                    handle = server.bundle(build_id)
                    if handle is not None and not handle.ready.is_set():
                        await asyncio.sleep(0.05)
                        continue
                if session.normalized.delivery is DeliveryMode.STREAM and execution is not None and not stream_finished:
                    await asyncio.sleep(0.05)
                    continue
                return
            await asyncio.sleep(0.05)
    except WebSocketDisconnect:
        if session.normalized.delivery is DeliveryMode.STREAM:
            server.cancel_build(build_id)


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


__all__ = ["build_events"]
