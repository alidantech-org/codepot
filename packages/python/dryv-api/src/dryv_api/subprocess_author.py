from __future__ import annotations

import base64
import json
import os
import subprocess
import threading
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

from dryv.features.authoring import (
    AuthorBackendHello,
    AuthorComplete,
    AuthorDiagnostic,
    AuthorDocument,
    AuthorMessage,
    AuthorProgress,
    AuthorRequest,
)

from .service import ApiContractError


class SubprocessAuthorSession:
    """Outer-host JSONL transport adapter for an independent Author Backend process."""

    def __init__(
        self,
        command: Sequence[str],
        *,
        resources: Mapping[str, tuple[str | None, bytes]],
        cwd: str | Path | None = None,
        env: Mapping[str, str] | None = None,
    ) -> None:
        if not command:
            raise ValueError("author backend command must not be empty")
        self._resources = dict(resources)
        process_env = os.environ.copy()
        if env is not None:
            process_env.update(env)
        self._process = subprocess.Popen(
            tuple(command),
            cwd=None if cwd is None else str(cwd),
            env=process_env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
        )
        self._lock = threading.Lock()
        self._hello: AuthorBackendHello | None = None

    def hello(self) -> AuthorBackendHello:
        if self._hello is not None:
            return self._hello
        response = self._exchange_one({"type": "hello"})
        if response.get("type") != "hello-result":
            raise ApiContractError("API_AUTHOR_PROTOCOL", "author backend did not return hello-result")
        try:
            hello = AuthorBackendHello(
                backend_id=_string(response, "backendId"),
                backend_version=_string(response, "backendVersion"),
                supported_source_kinds=_strings(response, "supportedSourceKinds"),
                supported_ir_versions=_strings(response, "supportedIrVersions"),
                protocol_versions=_ints(response, "protocolVersions"),
                streaming=_bool(response, "streaming"),
                fingerprint=_string(response, "fingerprint"),
                max_concurrency=_int(response, "maxConcurrency"),
            )
        except (TypeError, ValueError) as exc:
            raise ApiContractError("API_AUTHOR_HELLO", "author backend hello is invalid") from exc
        self._hello = hello
        return hello

    def author(self, request: AuthorRequest) -> Iterable[AuthorMessage]:
        sources: list[dict[str, object]] = []
        for source in request.sources:
            resource = self._resources.get(source.resource_id)
            if resource is None:
                raise ApiContractError(
                    "API_AUTHOR_RESOURCE_MISSING",
                    f"author source resource {source.resource_id!r} is not available to the connection",
                )
            media_type, content = resource
            sources.append(
                {
                    "resourceId": source.resource_id,
                    "mediaType": source.media_type or media_type,
                    "contentBase64": base64.b64encode(content).decode("ascii"),
                }
            )
        command = {
            "type": "author",
            "request": {
                "protocolVersion": request.protocol_version,
                "jobId": request.job_id,
                "requestedIrVersion": request.requested_ir_version,
                "sourceKind": request.source_kind,
                "sources": sources,
                "options": {name: value for name, value in request.options},
            },
        }
        with self._lock:
            self._write(command)
            while True:
                response = self._read()
                kind = response.get("type")
                if kind == "author-progress":
                    yield AuthorProgress(
                        _string(response, "message"),
                        _optional_int(response, "completed"),
                        _optional_int(response, "total"),
                    )
                elif kind == "author-diagnostic":
                    yield AuthorDiagnostic(
                        _string(response, "code"),
                        _string(response, "message"),
                        _string_default(response, "severity", "error"),
                    )
                elif kind == "author-document":
                    try:
                        content = base64.b64decode(
                            _string(response, "contentBase64"), validate=True
                        )
                    except Exception as exc:  # noqa: BLE001 - normalized transport error
                        raise ApiContractError(
                            "API_AUTHOR_BASE64",
                            "author document content is invalid base64",
                        ) from exc
                    yield AuthorDocument(_string(response, "mediaType"), content)
                elif kind == "author-complete":
                    yield AuthorComplete(
                        _string(response, "jobId"),
                        _string(response, "backendFingerprint"),
                    )
                    return
                elif kind == "protocol-error":
                    raise ApiContractError(
                        _string_default(response, "code", "API_AUTHOR_PROTOCOL"),
                        _string_default(response, "message", "author backend protocol error"),
                    )
                else:
                    raise ApiContractError(
                        "API_AUTHOR_PROTOCOL",
                        f"unknown author backend message {kind!r}",
                    )

    def cancel(self, job_id: str) -> None:
        if self._process.poll() is not None:
            return
        try:
            self._exchange_one({"type": "cancel", "jobId": job_id})
        except ApiContractError:
            return

    def close(self) -> None:
        if self._process.poll() is not None:
            return
        try:
            self._exchange_one({"type": "shutdown"})
        except ApiContractError:
            self._process.terminate()
        try:
            self._process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait(timeout=2)

    def __enter__(self) -> SubprocessAuthorSession:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self.close()

    def _exchange_one(self, document: Mapping[str, object]) -> dict[str, object]:
        with self._lock:
            self._write(document)
            return self._read()

    def _write(self, document: Mapping[str, object]) -> None:
        if self._process.poll() is not None:
            raise self._process_error("author backend exited")
        assert self._process.stdin is not None
        self._process.stdin.write(json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n")
        self._process.stdin.flush()

    def _read(self) -> dict[str, object]:
        assert self._process.stdout is not None
        line = self._process.stdout.readline()
        if not line:
            raise self._process_error("author backend closed the protocol stream")
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ApiContractError("API_AUTHOR_JSON", "author backend returned invalid JSON") from exc
        return _object(value, "response")

    def _process_error(self, prefix: str) -> ApiContractError:
        stderr = ""
        if self._process.stderr is not None:
            stderr = self._process.stderr.read().strip()
        return ApiContractError(
            "API_AUTHOR_PROCESS_EXIT",
            f"{prefix} with code {self._process.poll()}: {stderr}",
        )


def _object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ApiContractError("API_AUTHOR_PROTOCOL", f"{label} must be an object")
    return value


def _string(value: Mapping[str, object], key: str) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not result:
        raise ApiContractError("API_AUTHOR_PROTOCOL", f"{key} must be a non-empty string")
    return result


def _string_default(value: Mapping[str, object], key: str, default: str) -> str:
    result = value.get(key, default)
    if not isinstance(result, str) or not result:
        raise ApiContractError("API_AUTHOR_PROTOCOL", f"{key} must be a non-empty string")
    return result


def _strings(value: Mapping[str, object], key: str) -> tuple[str, ...]:
    raw = value.get(key)
    if not isinstance(raw, list) or not all(isinstance(item, str) and item for item in raw):
        raise ApiContractError("API_AUTHOR_PROTOCOL", f"{key} must be a string array")
    return tuple(raw)


def _ints(value: Mapping[str, object], key: str) -> tuple[int, ...]:
    raw = value.get(key)
    if not isinstance(raw, list) or not all(isinstance(item, int) and not isinstance(item, bool) for item in raw):
        raise ApiContractError("API_AUTHOR_PROTOCOL", f"{key} must be an integer array")
    return tuple(raw)


def _int(value: Mapping[str, object], key: str) -> int:
    result = value.get(key)
    if not isinstance(result, int) or isinstance(result, bool):
        raise ApiContractError("API_AUTHOR_PROTOCOL", f"{key} must be an integer")
    return result


def _optional_int(value: Mapping[str, object], key: str) -> int | None:
    result = value.get(key)
    if result is None:
        return None
    if not isinstance(result, int) or isinstance(result, bool):
        raise ApiContractError("API_AUTHOR_PROTOCOL", f"{key} must be an integer or null")
    return result


def _bool(value: Mapping[str, object], key: str) -> bool:
    result = value.get(key)
    if not isinstance(result, bool):
        raise ApiContractError("API_AUTHOR_PROTOCOL", f"{key} must be a boolean")
    return result


__all__ = ["SubprocessAuthorSession"]
