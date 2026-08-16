from __future__ import annotations

import socket
from dataclasses import dataclass


@dataclass(slots=True)
class ReservedPort:
    socket: socket.socket
    host: str
    port: int

    def close(self) -> None:
        self.socket.close()


def reserve_loopback_port() -> ReservedPort:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", 0))
    listener.listen(128)
    listener.set_inheritable(False)
    host, port = listener.getsockname()
    return ReservedPort(listener, str(host), int(port))


__all__ = ["ReservedPort", "reserve_loopback_port"]
