from __future__ import annotations

import base64
import hashlib
import json
import sys
from typing import Iterator

from . import Author, VERSION, __version__, dumps_json

_PROTOCOL_VERSION = 1
_SOURCE_KIND = "python"
_FINGERPRINT = "sha256:" + hashlib.sha256(
    f"dryv-author\0{__version__}\0python-backend-v1".encode("utf-8")
).hexdigest()
_cancelled: set[str] = set()


def main() -> int:
    for line in sys.stdin:
        try:
            message = json.loads(line)
            responses = tuple(_handle(message))
        except Exception as exc:  # noqa: BLE001 - keep backend protocol alive
            responses = (
                {
                    "type": "protocol-error",
                    "code": "AUTHOR_PROTOCOL_ERROR",
                    "message": str(exc) or type(exc).__name__,
                },
            )
        for response in responses:
            sys.stdout.write(json.dumps(response, separators=(",", ":"), sort_keys=True) + "\n")
            sys.stdout.flush()
        if responses and responses[-1].get("type") == "shutdown-result":
            return 0
    return 0


def _handle(message: object) -> Iterator[dict[str, object]]:
    if not isinstance(message, dict):
        raise ValueError("protocol message must be an object")
    kind = message.get("type")
    if kind == "hello":
        yield {
            "type": "hello-result",
            "backendId": "python-author",
            "backendVersion": __version__,
            "supportedSourceKinds": [_SOURCE_KIND],
            "supportedIrVersions": [VERSION],
            "protocolVersions": [_PROTOCOL_VERSION],
            "streaming": False,
            "fingerprint": _FINGERPRINT,
            "maxConcurrency": 1,
        }
        return
    if kind == "cancel":
        job_id = _string(message.get("jobId"), "jobId")
        _cancelled.add(job_id)
        yield {"type": "cancel-result", "jobId": job_id}
        return
    if kind == "shutdown":
        yield {"type": "shutdown-result"}
        return
    if kind != "author":
        raise ValueError(f"unknown protocol message type {kind!r}")

    request = message.get("request")
    if not isinstance(request, dict):
        raise ValueError("author request must be an object")
    job_id = _string(request.get("jobId"), "jobId")
    if job_id in _cancelled:
        yield {
            "type": "author-diagnostic",
            "code": "AUTHOR_CANCELLED",
            "message": "author job was cancelled",
            "severity": "error",
        }
        yield {"type": "author-complete", "jobId": job_id, "backendFingerprint": _FINGERPRINT}
        return
    if _string(request.get("sourceKind"), "sourceKind") != _SOURCE_KIND:
        raise ValueError("python author backend only supports sourceKind=python")
    sources = request.get("sources")
    if not isinstance(sources, list) or len(sources) != 1 or not isinstance(sources[0], dict):
        raise ValueError("python author backend requires exactly one logical source resource")
    source = sources[0]
    media_type = source.get("mediaType")
    if media_type not in {None, "text/x-python", "text/python"}:
        raise ValueError("python author source must use text/x-python")
    try:
        content = base64.b64decode(_string(source.get("contentBase64"), "source.contentBase64"), validate=True)
        text = content.decode("utf-8")
    except Exception as exc:  # noqa: BLE001
        raise ValueError("python author source must be valid base64 UTF-8") from exc

    yield {"type": "author-progress", "message": "compiling author source", "completed": 0, "total": 1}
    author = _execute_author_source(text, _string(source.get("resourceId"), "source.resourceId"))
    result = author.compile()
    for diagnostic in result.diagnostics:
        yield {
            "type": "author-diagnostic",
            "code": diagnostic.code,
            "message": diagnostic.message,
            "severity": diagnostic.severity.value,
        }
    if result.contract is not None:
        content_json = dumps_json(result.contract).encode("utf-8")
        yield {
            "type": "author-document",
            "mediaType": "application/vnd.dryv.ir+json",
            "contentBase64": base64.b64encode(content_json).decode("ascii"),
        }
    yield {"type": "author-progress", "message": "author source compiled", "completed": 1, "total": 1}
    yield {"type": "author-complete", "jobId": job_id, "backendFingerprint": _FINGERPRINT}


def _execute_author_source(source: str, resource_id: str) -> Author:
    namespace: dict[str, object] = {
        "__name__": "__dryv_author_source__",
        "__file__": resource_id,
    }
    exec(compile(source, resource_id, "exec"), namespace, namespace)  # noqa: S102 - execution is the Author Backend's purpose
    builder = namespace.get("build_author")
    if callable(builder):
        value = builder()
    else:
        value = namespace.get("AUTHOR")
    if not isinstance(value, Author):
        raise ValueError("python author source must expose build_author() -> Author or AUTHOR")
    return value


def _string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
