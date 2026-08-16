from __future__ import annotations

import base64
import json
import sys
from dataclasses import dataclass
from typing import Mapping

from .session import JinjaRenderSession


@dataclass(frozen=True, slots=True)
class _Output:
    id: str
    path: str


@dataclass(frozen=True, slots=True)
class _Request:
    job_id: str
    template_content: bytes
    context: Mapping[str, object]
    outputs: tuple[_Output, ...]


def main() -> int:
    session = JinjaRenderSession(max_concurrency=1)
    for line in sys.stdin:
        try:
            message = json.loads(line)
            response = _handle(session, message)
        except Exception as exc:  # noqa: BLE001 - process boundary must stay alive
            response = {
                "type": "protocol-error",
                "code": "JINJA_PROTOCOL_ERROR",
                "message": str(exc) or type(exc).__name__,
            }
        sys.stdout.write(json.dumps(response, separators=(",", ":"), sort_keys=True) + "\n")
        sys.stdout.flush()
        if response.get("type") == "shutdown-result":
            return 0
    return 0


def _handle(session: JinjaRenderSession, message: object) -> dict[str, object]:
    if not isinstance(message, dict):
        raise ValueError("protocol message must be an object")
    kind = message.get("type")
    if kind == "hello":
        hello = session.hello()
        return {
            "type": "hello-result",
            "rendererId": hello.renderer_id,
            "rendererVersion": hello.renderer_version,
            "capabilities": list(hello.capabilities),
            "protocolVersions": list(hello.protocol_versions),
            "contextVersions": list(hello.context_versions),
            "templateMediaTypes": list(hello.template_media_types),
            "fingerprint": hello.fingerprint,
            "maxConcurrency": hello.max_concurrency,
            "deterministic": hello.deterministic,
        }
    if kind == "cancel":
        job_id = _string(message.get("jobId"), "jobId")
        session.cancel(job_id)
        return {"type": "cancel-result", "jobId": job_id}
    if kind == "shutdown":
        return {"type": "shutdown-result"}
    if kind != "render":
        raise ValueError(f"unknown protocol message type {kind!r}")

    raw = message.get("request")
    if not isinstance(raw, dict):
        raise ValueError("render request must be an object")
    try:
        template = base64.b64decode(_string(raw.get("templateContentBase64"), "templateContentBase64"), validate=True)
    except Exception as exc:  # noqa: BLE001
        raise ValueError("templateContentBase64 is invalid") from exc
    context = raw.get("context")
    if not isinstance(context, dict) or not all(isinstance(key, str) for key in context):
        raise ValueError("context must be a string-keyed object")
    outputs_raw = raw.get("outputs")
    if not isinstance(outputs_raw, list):
        raise ValueError("outputs must be an array")
    outputs = tuple(
        _Output(_string(item.get("id"), "output.id"), _string(item.get("path"), "output.path"))
        for item in outputs_raw
        if isinstance(item, dict)
    )
    if len(outputs) != len(outputs_raw):
        raise ValueError("outputs must contain objects")
    request = _Request(
        _string(raw.get("jobId"), "jobId"),
        template,
        context,
        outputs,
    )
    result = session.render(request)
    return {
        "type": "render-result",
        "jobId": result.job_id,
        "rendererFingerprint": result.renderer_fingerprint,
        "outputs": [
            {
                "id": item.id,
                "contentBase64": base64.b64encode(item.content).decode("ascii"),
                "contentHash": item.content_hash,
            }
            for item in result.outputs
        ],
        "diagnostics": [
            {"code": item.code, "message": item.message, "severity": item.severity}
            for item in result.diagnostics
        ],
        "cancelled": result.cancelled,
    }


def _string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
