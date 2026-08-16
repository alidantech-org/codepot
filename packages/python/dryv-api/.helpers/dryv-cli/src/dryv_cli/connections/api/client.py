from __future__ import annotations

from collections.abc import Iterator
from typing import BinaryIO

from dryv_api import BuildSummary, CreateBuildRequest

from .events import ApiEvent
from .http import ApiHttpTransport, BundleDownload
from .websocket import ApiWebSocketTransport


class DryvApiClient:
    """Typed synchronous Project Client boundary for dryv-api."""

    def __init__(self, base_url: str, *, timeout: float = 30.0) -> None:
        self.http = ApiHttpTransport(base_url, timeout=timeout)
        self.websocket = ApiWebSocketTransport(base_url)

    def close(self) -> None:
        self.http.close()

    def create_build(self, request: CreateBuildRequest) -> BuildSummary:
        return self.http.create_build(request)

    def get_build(self, build_id: str) -> BuildSummary:
        return self.http.get_build(build_id)

    def get_plan(self, build_id: str) -> dict[str, object]:
        return self.http.get_plan(build_id)

    def preflight(self, build_id: str) -> BuildSummary:
        return self.http.preflight(build_id)

    def render(self, build_id: str) -> BuildSummary:
        return self.http.render(build_id)

    def events(self, build_id: str) -> Iterator[ApiEvent]:
        return self.websocket.events(build_id)

    def download_bundle(self, build_id: str, target: BinaryIO) -> BundleDownload:
        return self.http.download_bundle(build_id, target)

    def cancel(self, build_id: str) -> BuildSummary:
        return self.http.cancel(build_id)

    def release(self, build_id: str) -> None:
        self.http.release(build_id)


__all__ = ["DryvApiClient"]
