from __future__ import annotations

import sys
import time
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from dryv_api.server import DryvApiServer

from .process import LocalProcessError, OwnedProcess


class LocalRendererError(RuntimeError):
    pass


class LocalRendererManager:
    def __init__(self, base_url: str, server: DryvApiServer) -> None:
        self.base_url = base_url
        self.server = server
        self._processes: dict[str, OwnedProcess] = {}

    def ensure(self, capabilities: tuple[str, ...], *, timeout: float = 10.0) -> None:
        for capability in sorted(set(capabilities)):
            if self.server.renderers.compatible(capability):
                continue
            if capability != "jinja":
                raise LocalRendererError(f"no local renderer helper is installed for capability {capability!r}")
            self._start_jinja()
            self._wait_for(capability, timeout=timeout)

    def stop(self) -> None:
        for capability, process in reversed(tuple(self._processes.items())):
            process.stop()
            self._processes.pop(capability, None)

    def _start_jinja(self) -> None:
        if "jinja" in self._processes:
            self._processes["jinja"].require_running()
            return
        process = OwnedProcess(
            (
                sys.executable,
                "-m",
                "dryv_template_jinja",
                "--api",
                _renderer_url(self.base_url),
                "--connection-id",
                "local-jinja",
            ),
            cwd=Path.cwd(),
        )
        process.start()
        self._processes["jinja"] = process

    def _wait_for(self, capability: str, *, timeout: float) -> None:
        deadline = time.monotonic() + timeout
        while not self.server.renderers.compatible(capability):
            process = self._processes.get(capability)
            if process is not None:
                try:
                    process.require_running()
                except LocalProcessError as exc:
                    raise LocalRendererError(f"local renderer for {capability!r} exited: {exc.stderr.strip()}") from exc
            if time.monotonic() >= deadline:
                raise LocalRendererError(f"local renderer for {capability!r} did not register with dryv-api")
            time.sleep(0.02)


def _renderer_url(base_url: str) -> str:
    parsed = urlsplit(base_url)
    scheme = "wss" if parsed.scheme == "https" else "ws"
    return urlunsplit((scheme, parsed.netloc, parsed.path.rstrip("/") + "/v1/renderers", "", ""))


__all__ = ["LocalRendererError", "LocalRendererManager"]
