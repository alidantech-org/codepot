from __future__ import annotations

import time
from threading import Thread

import uvicorn

from dryv_api.server import DryvApiServer
from dryv_api.transport import create_app

from .ports import ReservedPort, reserve_loopback_port


class LocalApiError(RuntimeError):
    pass


class LocalApiHost:
    def __init__(self) -> None:
        self.dryv_server = DryvApiServer()
        self._reserved: ReservedPort | None = None
        self._uvicorn: uvicorn.Server | None = None
        self._thread: Thread | None = None

    @property
    def base_url(self) -> str:
        reserved = self._reserved
        if reserved is None:
            raise RuntimeError("local dryv-api is not started")
        return f"http://{reserved.host}:{reserved.port}"

    def start(self, *, timeout: float = 10.0) -> str:
        if self._thread is not None:
            return self.base_url
        reserved = reserve_loopback_port()
        app = create_app(self.dryv_server)
        config = uvicorn.Config(app, log_level="warning", lifespan="off", access_log=False)
        server = uvicorn.Server(config)
        thread = Thread(
            target=server.run,
            kwargs={"sockets": [reserved.socket]},
            name="dryv-local-api",
            daemon=True,
        )
        self._reserved = reserved
        self._uvicorn = server
        self._thread = thread
        thread.start()
        deadline = time.monotonic() + timeout
        while not server.started:
            if not thread.is_alive():
                self.stop()
                raise LocalApiError("local dryv-api stopped during startup")
            if time.monotonic() >= deadline:
                self.stop()
                raise LocalApiError("local dryv-api did not become ready")
            time.sleep(0.02)
        return self.base_url

    def stop(self, *, timeout: float = 5.0) -> None:
        server = self._uvicorn
        thread = self._thread
        reserved = self._reserved
        self._uvicorn = None
        self._thread = None
        self._reserved = None
        if server is not None:
            server.should_exit = True
        if thread is not None and thread.is_alive():
            thread.join(timeout=timeout)
        if reserved is not None:
            try:
                reserved.close()
            except OSError:
                pass


__all__ = ["LocalApiError", "LocalApiHost"]
