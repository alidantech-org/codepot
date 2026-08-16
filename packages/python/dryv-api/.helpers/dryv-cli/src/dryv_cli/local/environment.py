from __future__ import annotations

from dataclasses import dataclass

from dryv_cli.connections.api import DryvApiClient

from .api import LocalApiHost
from .renderer import LocalRendererManager


@dataclass(slots=True)
class LocalEnvironment:
    external_api: str | None = None
    api_host: LocalApiHost | None = None
    api_client: DryvApiClient | None = None
    renderers: LocalRendererManager | None = None
    _owned: bool = False

    def __enter__(self) -> LocalEnvironment:
        self.start()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    @property
    def api(self) -> DryvApiClient:
        if self.api_client is None:
            raise RuntimeError("Dryv environment is not started")
        return self.api_client

    def start(self) -> DryvApiClient:
        if self.api_client is not None:
            return self.api_client
        if self.external_api is not None:
            self.api_client = DryvApiClient(self.external_api)
            self._owned = False
            return self.api_client
        host = LocalApiHost()
        base_url = host.start()
        self.api_host = host
        self.api_client = DryvApiClient(base_url)
        self.renderers = LocalRendererManager(base_url, host.dryv_server)
        self._owned = True
        return self.api_client

    def ensure_renderers(self, capabilities: tuple[str, ...]) -> None:
        if not capabilities or self.renderers is None:
            return
        self.renderers.ensure(capabilities)

    def close(self) -> None:
        if self.renderers is not None:
            self.renderers.stop()
            self.renderers = None
        if self.api_client is not None:
            self.api_client.close()
            self.api_client = None
        if self._owned and self.api_host is not None:
            self.api_host.stop()
        self.api_host = None
        self._owned = False


__all__ = ["LocalEnvironment"]
