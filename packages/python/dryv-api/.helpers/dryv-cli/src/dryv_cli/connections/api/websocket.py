from __future__ import annotations

import json
from collections.abc import Iterator
from urllib.parse import urlsplit, urlunsplit

from websockets.sync.client import connect

from .events import ApiEvent, decode_event


class ApiWebSocketTransport:
    def __init__(self, base_url: str, *, open_timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.open_timeout = open_timeout

    def events(self, build_id: str) -> Iterator[ApiEvent]:
        url = _websocket_url(self.base_url, f"/v1/builds/{build_id}/events")
        with connect(url, open_timeout=self.open_timeout, max_size=2 * 1024 * 1024) as socket:
            for message in socket:
                if not isinstance(message, str):
                    raise RuntimeError("dryv-api event WebSocket must use JSON text frames")
                try:
                    yield decode_event(json.loads(message))
                except json.JSONDecodeError as exc:
                    raise RuntimeError("dryv-api event WebSocket returned invalid JSON") from exc


def _websocket_url(base_url: str, path: str) -> str:
    parsed = urlsplit(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("dryv-api base URL must use http or https")
    scheme = "wss" if parsed.scheme == "https" else "ws"
    prefix = parsed.path.rstrip("/")
    return urlunsplit((scheme, parsed.netloc, prefix + path, "", ""))


__all__ = ["ApiWebSocketTransport"]
