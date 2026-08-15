from __future__ import annotations

import json
import os
import subprocess
import threading
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path


class ApiTransportError(RuntimeError):
    pass


class StdioApiTransport:
    """Project Client transport for a remote-capable dryv-api JSONL host."""

    def __init__(
        self,
        command: Sequence[str],
        *,
        cwd: str | Path | None = None,
        env: Mapping[str, str] | None = None,
    ) -> None:
        if not command:
            raise ValueError("API host command must not be empty")
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
        self._write_lock = threading.Lock()
        self._read_lock = threading.Lock()

    def hello(self) -> dict[str, object]:
        self._write({"type": "hello"})
        response = self._read()
        if response.get("type") != "hello-result":
            raise ApiTransportError(f"unexpected API hello response: {response!r}")
        return response

    def build_events(self, request: Mapping[str, object]) -> Iterator[dict[str, object]]:
        build_id = request.get("buildId")
        if not isinstance(build_id, str) or not build_id:
            raise ValueError("build request requires buildId")
        self._write({"type": "build", "request": dict(request)})
        with self._read_lock:
            while True:
                message = self._read_unlocked()
                kind = message.get("type")
                if kind == "build-event" and message.get("buildId") == build_id:
                    event = message.get("event")
                    if not isinstance(event, dict):
                        raise ApiTransportError("API build-event payload is not an object")
                    yield event
                    continue
                if kind == "build-error" and message.get("buildId") == build_id:
                    raise ApiTransportError(
                        f"{message.get('code', 'DRYV_API_BUILD_ERROR')}: {message.get('message', 'build failed')}"
                    )
                if kind == "build-finished" and message.get("buildId") == build_id:
                    return
                if kind == "host-error":
                    raise ApiTransportError(
                        f"{message.get('code', 'DRYV_API_HOST_ERROR')}: {message.get('message', 'host failed')}"
                    )
                # A cancel acknowledgement or another build's event may be consumed by
                # another caller only when transports are multiplexed. This compact
                # Project Client intentionally supports one active build reader.

    def cancel(self, build_id: str) -> None:
        if not build_id:
            raise ValueError("build_id must not be empty")
        self._write({"type": "cancel", "buildId": build_id})

    def close(self) -> None:
        if self._process.poll() is not None:
            return
        self._write({"type": "shutdown"})
        try:
            self._process.wait(timeout=4)
        except subprocess.TimeoutExpired:
            self._process.terminate()
            try:
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait(timeout=2)

    def __enter__(self) -> StdioApiTransport:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self.close()

    def _write(self, document: Mapping[str, object]) -> None:
        with self._write_lock:
            if self._process.poll() is not None:
                raise self._process_error("API host exited")
            assert self._process.stdin is not None
            self._process.stdin.write(json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n")
            self._process.stdin.flush()

    def _read(self) -> dict[str, object]:
        with self._read_lock:
            return self._read_unlocked()

    def _read_unlocked(self) -> dict[str, object]:
        assert self._process.stdout is not None
        line = self._process.stdout.readline()
        if not line:
            raise self._process_error("API host closed stdout")
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ApiTransportError("API host returned invalid JSON") from exc
        if not isinstance(value, dict):
            raise ApiTransportError("API host response must be an object")
        return value

    def _process_error(self, prefix: str) -> ApiTransportError:
        stderr = ""
        if self._process.stderr is not None:
            stderr = self._process.stderr.read().strip()
        return ApiTransportError(
            f"{prefix} with code {self._process.poll()}: {stderr}"
        )


__all__ = ["ApiTransportError", "StdioApiTransport"]
