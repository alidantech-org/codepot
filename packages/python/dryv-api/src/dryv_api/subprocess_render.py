from __future__ import annotations

import base64
import json
import os
import subprocess
import threading
from collections.abc import Mapping, Sequence
from pathlib import Path

from dryv.features.templating import (
    RenderDiagnostic,
    RenderResult,
    RenderedOutput,
    RendererHello,
)

from .service import ApiContractError


class SubprocessRenderSession:
    """Outer-host JSONL transport adapter for an independent Render Client process."""

    def __init__(
        self,
        command: Sequence[str],
        *,
        cwd: str | Path | None = None,
        env: Mapping[str, str] | None = None,
    ) -> None:
        if not command:
            raise ValueError("render client command must not be empty")
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
        self._hello: RendererHello | None = None

    def hello(self) -> RendererHello:
        if self._hello is not None:
            return self._hello
        response = self._exchange({"type": "hello"})
        if response.get("type") != "hello-result":
            raise ApiContractError("API_RENDER_PROTOCOL", "render client did not return hello-result")
        try:
            hello = RendererHello(
                renderer_id=_string(response, "rendererId"),
                renderer_version=_string(response, "rendererVersion"),
                capabilities=_strings(response, "capabilities"),
                protocol_versions=_ints(response, "protocolVersions"),
                context_versions=_ints(response, "contextVersions"),
                template_media_types=_strings(response, "templateMediaTypes"),
                fingerprint=_string(response, "fingerprint"),
                max_concurrency=_int(response, "maxConcurrency"),
                deterministic=_bool(response, "deterministic"),
            )
        except (TypeError, ValueError) as exc:
            raise ApiContractError("API_RENDER_HELLO", "render client hello is invalid") from exc
        self._hello = hello
        return hello

    def render(self, request: object) -> RenderResult:
        outputs = tuple(getattr(request, "outputs"))
        options = tuple(getattr(request, "options", ()))
        document = {
            "type": "render",
            "request": {
                "protocolVersion": getattr(request, "protocol_version"),
                "contextVersion": getattr(request, "context_version"),
                "jobId": getattr(request, "job_id"),
                "requiredCapability": getattr(request, "required_capability"),
                "templateResourceId": getattr(request, "template_resource_id"),
                "templateMediaType": getattr(request, "template_media_type"),
                "templateContentBase64": base64.b64encode(
                    getattr(request, "template_content")
                ).decode("ascii"),
                "templateHash": getattr(request, "template_hash"),
                "context": getattr(request, "context"),
                "contextHash": getattr(request, "context_hash"),
                "outputs": [
                    {"id": item.id, "path": item.path}
                    for item in outputs
                ],
                "options": {name: value for name, value in options},
            },
        }
        response = self._exchange(document)
        if response.get("type") != "render-result":
            raise ApiContractError("API_RENDER_PROTOCOL", "render client did not return render-result")
        raw_outputs = response.get("outputs", [])
        raw_diagnostics = response.get("diagnostics", [])
        if not isinstance(raw_outputs, list) or not isinstance(raw_diagnostics, list):
            raise ApiContractError("API_RENDER_PROTOCOL", "render result arrays are invalid")
        rendered: list[RenderedOutput] = []
        for index, raw in enumerate(raw_outputs):
            item = _object(raw, f"outputs[{index}]")
            try:
                content = base64.b64decode(_string(item, "contentBase64"), validate=True)
            except Exception as exc:  # noqa: BLE001 - normalized transport error
                raise ApiContractError("API_RENDER_BASE64", "rendered content is invalid base64") from exc
            rendered.append(
                RenderedOutput(
                    _string(item, "id"),
                    content,
                    _string(item, "contentHash"),
                )
            )
        diagnostics = tuple(
            RenderDiagnostic(
                _string(item, "code"),
                _string(item, "message"),
                _string_default(item, "severity", "error"),
            )
            for index, raw in enumerate(raw_diagnostics)
            for item in (_object(raw, f"diagnostics[{index}]"),)
        )
        return RenderResult(
            job_id=_string(response, "jobId"),
            renderer_fingerprint=_string(response, "rendererFingerprint"),
            outputs=tuple(rendered),
            diagnostics=diagnostics,
            cancelled=_bool_default(response, "cancelled", False),
        )

    def cancel(self, job_id: str) -> None:
        # One process connection is serialized, so cancellation is best-effort between requests.
        if self._process.poll() is not None:
            return
        try:
            self._exchange({"type": "cancel", "jobId": job_id})
        except ApiContractError:
            return

    def close(self) -> None:
        if self._process.poll() is not None:
            return
        try:
            self._exchange({"type": "shutdown"})
        except ApiContractError:
            self._process.terminate()
        try:
            self._process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait(timeout=2)

    def __enter__(self) -> SubprocessRenderSession:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self.close()

    def _exchange(self, document: Mapping[str, object]) -> dict[str, object]:
        with self._lock:
            if self._process.poll() is not None:
                stderr = ""
                if self._process.stderr is not None:
                    stderr = self._process.stderr.read().strip()
                raise ApiContractError(
                    "API_RENDER_PROCESS_EXIT",
                    f"render client exited with code {self._process.returncode}: {stderr}",
                )
            assert self._process.stdin is not None
            assert self._process.stdout is not None
            self._process.stdin.write(json.dumps(document, separators=(",", ":"), sort_keys=True) + "\n")
            self._process.stdin.flush()
            line = self._process.stdout.readline()
            if not line:
                stderr = ""
                if self._process.stderr is not None:
                    stderr = self._process.stderr.read().strip()
                raise ApiContractError(
                    "API_RENDER_EOF",
                    f"render client closed the protocol stream: {stderr}",
                )
            try:
                response = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ApiContractError("API_RENDER_JSON", "render client returned invalid JSON") from exc
            return _object(response, "response")


def _object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ApiContractError("API_RENDER_PROTOCOL", f"{label} must be an object")
    return value


def _string(value: Mapping[str, object], key: str) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not result:
        raise ApiContractError("API_RENDER_PROTOCOL", f"{key} must be a non-empty string")
    return result


def _string_default(value: Mapping[str, object], key: str, default: str) -> str:
    result = value.get(key, default)
    if not isinstance(result, str) or not result:
        raise ApiContractError("API_RENDER_PROTOCOL", f"{key} must be a non-empty string")
    return result


def _strings(value: Mapping[str, object], key: str) -> tuple[str, ...]:
    raw = value.get(key)
    if not isinstance(raw, list) or not all(isinstance(item, str) and item for item in raw):
        raise ApiContractError("API_RENDER_PROTOCOL", f"{key} must be a string array")
    return tuple(raw)


def _ints(value: Mapping[str, object], key: str) -> tuple[int, ...]:
    raw = value.get(key)
    if not isinstance(raw, list) or not all(isinstance(item, int) and not isinstance(item, bool) for item in raw):
        raise ApiContractError("API_RENDER_PROTOCOL", f"{key} must be an integer array")
    return tuple(raw)


def _int(value: Mapping[str, object], key: str) -> int:
    result = value.get(key)
    if not isinstance(result, int) or isinstance(result, bool):
        raise ApiContractError("API_RENDER_PROTOCOL", f"{key} must be an integer")
    return result


def _bool(value: Mapping[str, object], key: str) -> bool:
    result = value.get(key)
    if not isinstance(result, bool):
        raise ApiContractError("API_RENDER_PROTOCOL", f"{key} must be a boolean")
    return result


def _bool_default(value: Mapping[str, object], key: str, default: bool) -> bool:
    result = value.get(key, default)
    if not isinstance(result, bool):
        raise ApiContractError("API_RENDER_PROTOCOL", f"{key} must be a boolean")
    return result


__all__ = ["SubprocessRenderSession"]
