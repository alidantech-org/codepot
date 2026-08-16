from __future__ import annotations

import base64
import json
import os
import sys
import threading
from collections.abc import Mapping

from dryv.runtime import DryvRuntime

from .service import DryvApiService, SessionRegistry
from .subprocess_author import SubprocessAuthorSession
from .subprocess_render import SubprocessRenderSession


class _Host:
    def __init__(self) -> None:
        self.runtime = DryvRuntime()
        self.renderers = _load_renderers()
        self.author_configs = _load_configs("DRYV_AUTHOR_CONNECTIONS_JSON")
        self.active: dict[str, DryvApiService] = {}
        self.threads: dict[str, threading.Thread] = {}
        self.lock = threading.Lock()
        self.output_lock = threading.Lock()

    def run(self) -> int:
        for line in sys.stdin:
            try:
                message = json.loads(line)
                self._handle(message)
            except Exception as exc:  # noqa: BLE001 - host must preserve protocol stream
                self._write(
                    {
                        "type": "host-error",
                        "code": "DRYV_API_HOST_ERROR",
                        "message": str(exc) or type(exc).__name__,
                    }
                )
        self.shutdown()
        return 0

    def _handle(self, message: object) -> None:
        if not isinstance(message, dict):
            raise ValueError("host message must be an object")
        kind = message.get("type")
        if kind == "hello":
            self._write(
                {
                    "type": "hello-result",
                    "host": "dryv-api",
                    "protocolVersion": 1,
                    "runtime": self.runtime.snapshot().core_version,
                    "renderConnections": sorted(self.renderers),
                    "authorConnections": sorted(self.author_configs),
                }
            )
            return
        if kind == "build":
            request = message.get("request")
            if not isinstance(request, dict):
                raise ValueError("build request must be an object")
            build_id = request.get("buildId")
            if not isinstance(build_id, str) or not build_id:
                raise ValueError("build request requires buildId")
            with self.lock:
                if build_id in self.active:
                    raise ValueError(f"build {build_id!r} is already active")
            thread = threading.Thread(
                target=self._run_build,
                args=(build_id, request),
                name=f"dryv-api-{build_id}",
                daemon=True,
            )
            with self.lock:
                self.threads[build_id] = thread
            thread.start()
            return
        if kind == "cancel":
            build_id = message.get("buildId")
            if not isinstance(build_id, str) or not build_id:
                raise ValueError("cancel requires buildId")
            with self.lock:
                service = self.active.get(build_id)
            cancelled = False if service is None else service.cancel(build_id)
            self._write({"type": "cancel-result", "buildId": build_id, "cancelled": cancelled})
            return
        if kind == "shutdown":
            self.shutdown()
            self._write({"type": "shutdown-result"})
            raise SystemExit(0)
        raise ValueError(f"unknown host message type {kind!r}")

    def _run_build(self, build_id: str, request: dict[str, object]) -> None:
        author_session: SubprocessAuthorSession | None = None
        try:
            registry = SessionRegistry()
            for identity, session in sorted(self.renderers.items()):
                registry.register_renderer(identity, session)

            author_value = request.get("author")
            if author_value is not None:
                if not isinstance(author_value, dict):
                    raise ValueError("author must be an object")
                connection_id = author_value.get("connectionId")
                if not isinstance(connection_id, str) or not connection_id:
                    raise ValueError("author.connectionId must be a non-empty string")
                config = self.author_configs.get(connection_id)
                if config is None:
                    raise ValueError(f"author connection {connection_id!r} is not configured")
                author_session = SubprocessAuthorSession(
                    config["command"],
                    cwd=config.get("cwd"),
                    env=config.get("env"),
                    resources=_author_resources(request),
                )
                registry.register_author(connection_id, author_session)

            service = DryvApiService(runtime=self.runtime, sessions=registry)
            with self.lock:
                self.active[build_id] = service
            for event in service.build_events(request):
                self._write({"type": "build-event", "buildId": build_id, "event": event})
            self._write({"type": "build-finished", "buildId": build_id})
        except Exception as exc:  # noqa: BLE001 - normalize outer-host failure
            self._write(
                {
                    "type": "build-error",
                    "buildId": build_id,
                    "code": getattr(exc, "code", "DRYV_API_BUILD_ERROR"),
                    "message": str(exc) or type(exc).__name__,
                }
            )
            self._write({"type": "build-finished", "buildId": build_id})
        finally:
            if author_session is not None:
                author_session.close()
            with self.lock:
                self.active.pop(build_id, None)
                self.threads.pop(build_id, None)

    def shutdown(self) -> None:
        with self.lock:
            active = tuple(self.active.items())
            threads = tuple(self.threads.values())
        for build_id, service in active:
            service.cancel(build_id)
        for thread in threads:
            if thread is not threading.current_thread():
                thread.join(timeout=3)
        for session in self.renderers.values():
            session.close()

    def _write(self, document: Mapping[str, object]) -> None:
        with self.output_lock:
            sys.stdout.write(json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n")
            sys.stdout.flush()


def _load_renderers() -> dict[str, SubprocessRenderSession]:
    result: dict[str, SubprocessRenderSession] = {}
    for config in _load_configs("DRYV_RENDER_CONNECTIONS_JSON").values():
        identity = config["id"]
        result[identity] = SubprocessRenderSession(
            config["command"],
            cwd=config.get("cwd"),
            env=config.get("env"),
        )
    return result


def _load_configs(name: str) -> dict[str, dict[str, object]]:
    raw = os.environ.get(name, "[]")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{name} must be valid JSON") from exc
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a JSON array")
    result: dict[str, dict[str, object]] = {}
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"{name}[{index}] must be an object")
        identity = item.get("id")
        command = item.get("command")
        if not isinstance(identity, str) or not identity:
            raise ValueError(f"{name}[{index}].id must be a non-empty string")
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
            raise ValueError(f"{name}[{index}].command must be a non-empty string array")
        cwd = item.get("cwd")
        if cwd is not None and not isinstance(cwd, str):
            raise ValueError(f"{name}[{index}].cwd must be a string")
        env = item.get("env", {})
        if not isinstance(env, dict) or not all(isinstance(key, str) and isinstance(val, str) for key, val in env.items()):
            raise ValueError(f"{name}[{index}].env must be a string map")
        if identity in result:
            raise ValueError(f"duplicate configured connection {identity!r}")
        result[identity] = {"id": identity, "command": tuple(command), "cwd": cwd, "env": env}
    return result


def _author_resources(request: Mapping[str, object]) -> dict[str, tuple[str | None, bytes]]:
    raw = request.get("resources", [])
    if not isinstance(raw, list):
        raise ValueError("resources must be an array")
    result: dict[str, tuple[str | None, bytes]] = {}
    for item in raw:
        if not isinstance(item, dict):
            continue
        identity = item.get("resourceId")
        encoded = item.get("contentBase64")
        media_type = item.get("mediaType")
        if not isinstance(identity, str) or not isinstance(encoded, str):
            continue
        if media_type is not None and not isinstance(media_type, str):
            continue
        try:
            content = base64.b64decode(encoded, validate=True)
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"invalid base64 resource {identity!r}") from exc
        result[identity] = (media_type, content)
    return result


def main() -> int:
    try:
        return _Host().run()
    except SystemExit as exc:
        return int(exc.code or 0)


if __name__ == "__main__":
    raise SystemExit(main())
