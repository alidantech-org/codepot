from __future__ import annotations

from threading import Lock

from dryv_api.contracts import ApiContractError

from .connection import RendererConnection, RendererConnectionState


class RendererRegistry:
    """Current external Render Client inventory, indexed only by capability."""

    def __init__(self) -> None:
        self._connections: dict[str, RendererConnection] = {}
        self._lock = Lock()

    def register(self, connection: RendererConnection) -> None:
        with self._lock:
            if connection.connection_id in self._connections:
                raise ApiContractError(
                    "API_RENDERER_CONNECTION_EXISTS",
                    f"renderer connection {connection.connection_id!r} already exists",
                )
            self._connections[connection.connection_id] = connection

    def unregister(self, connection_id: str, *, close: bool = True) -> bool:
        with self._lock:
            connection = self._connections.pop(connection_id, None)
        if connection is None:
            return False
        connection.close(close_transport=close)
        return True

    def get(self, connection_id: str) -> RendererConnection | None:
        with self._lock:
            return self._connections.get(connection_id)

    def require(self, connection_id: str) -> RendererConnection:
        connection = self.get(connection_id)
        if connection is None:
            raise ApiContractError(
                "API_RENDERER_CONNECTION_MISSING",
                f"renderer connection {connection_id!r} does not exist",
            )
        return connection

    def compatible(self, capability: str) -> tuple[RendererConnection, ...]:
        with self._lock:
            candidates = tuple(self._connections.values())
        return tuple(
            sorted(
                (
                    item
                    for item in candidates
                    if item.state is RendererConnectionState.READY
                    and capability in item.hello.capabilities
                ),
                key=lambda item: item.connection_id,
            )
        )

    def require_capability(self, capability: str) -> tuple[RendererConnection, ...]:
        connections = self.compatible(capability)
        if not connections:
            raise ApiContractError(
                "API_RENDERER_UNAVAILABLE",
                f"no connected Render Client provides capability {capability!r}",
            )
        return connections

    def first_compatible(self, capability: str) -> RendererConnection:
        return self.require_capability(capability)[0]

    def connection_ids(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._connections))


__all__ = ["RendererRegistry"]
