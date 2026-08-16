from __future__ import annotations

from dataclasses import dataclass
from queue import Empty, Full, Queue
from threading import Event
from typing import Iterator, TypeAlias

_DEFAULT_CHUNK_BYTES = 64 * 1024
_DEFAULT_QUEUE_CHUNKS = 32
_SENTINEL = object()


class ArtifactStreamCancelled(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ArtifactStarted:
    job_id: str
    artifact_id: str
    plan_index: int
    path: str
    dependencies: tuple[str, ...]
    media_type: str
    size: int | None = None


@dataclass(frozen=True, slots=True)
class ArtifactData:
    job_id: str
    artifact_id: str
    plan_index: int
    offset: int
    content: bytes


@dataclass(frozen=True, slots=True)
class ArtifactFinished:
    job_id: str
    artifact_id: str
    plan_index: int
    path: str
    size: int
    content_hash: str


ArtifactDeliveryEvent: TypeAlias = ArtifactStarted | ArtifactData | ArtifactFinished


class ArtifactStream:
    """Bounded producer/consumer channel for generated artifact delivery."""

    def __init__(
        self,
        *,
        max_chunk_bytes: int = _DEFAULT_CHUNK_BYTES,
        max_queued_chunks: int = _DEFAULT_QUEUE_CHUNKS,
    ) -> None:
        if max_chunk_bytes < 1 or max_queued_chunks < 1:
            raise ValueError("artifact stream limits must be positive")
        self.max_chunk_bytes = max_chunk_bytes
        self._queue: Queue[ArtifactDeliveryEvent | object] = Queue(maxsize=max_queued_chunks)
        self._cancelled = Event()
        self._closed = Event()

    @property
    def cancelled(self) -> bool:
        return self._cancelled.is_set()

    @property
    def closed(self) -> bool:
        return self._closed.is_set()

    def publish(self, event: ArtifactDeliveryEvent) -> None:
        if isinstance(event, ArtifactData) and len(event.content) > self.max_chunk_bytes:
            raise ValueError("artifact data exceeds stream max_chunk_bytes")
        while True:
            if self.cancelled:
                raise ArtifactStreamCancelled("artifact stream was cancelled")
            if self.closed:
                raise RuntimeError("artifact stream is closed")
            try:
                self._queue.put(event, timeout=0.1)
                return
            except Full:
                continue

    def close(self) -> None:
        if self._closed.is_set():
            return
        self._closed.set()
        self._put_sentinel()

    def cancel(self) -> None:
        if self._cancelled.is_set():
            return
        self._cancelled.set()
        self._closed.set()
        while True:
            try:
                self._queue.get_nowait()
            except Empty:
                break
        try:
            self._queue.put_nowait(_SENTINEL)
        except Full:
            pass

    def receive(self, *, timeout: float | None = None) -> ArtifactDeliveryEvent | None:
        try:
            value = self._queue.get(timeout=timeout)
        except Empty:
            return None
        if value is _SENTINEL:
            return None
        return value  # type: ignore[return-value]

    def __iter__(self) -> Iterator[ArtifactDeliveryEvent]:
        while True:
            if self.cancelled and self._queue.empty():
                return
            try:
                value = self._queue.get(timeout=0.1)
            except Empty:
                if self.closed:
                    return
                continue
            if value is _SENTINEL:
                return
            yield value  # type: ignore[misc]

    def _put_sentinel(self) -> None:
        while not self.cancelled:
            try:
                self._queue.put(_SENTINEL, timeout=0.1)
                return
            except Full:
                continue


__all__ = [
    "ArtifactData",
    "ArtifactDeliveryEvent",
    "ArtifactFinished",
    "ArtifactStarted",
    "ArtifactStream",
    "ArtifactStreamCancelled",
]
