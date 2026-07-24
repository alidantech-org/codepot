from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from queue import Empty, Full, Queue
from threading import Condition, Lock, Thread

from contracts.emission import EmissionFile, EmissionWriteResult
from contracts.paths import PathLifecycleMode
from emission.writer.file_writer import write_bytes_if_changed, write_text_if_changed

_SENTINEL = object()


class GraphQueueError(RuntimeError):
    """Raised when a generated-file queue worker fails."""


@dataclass(frozen=True, slots=True)
class GraphQueueLimits:
    """Bounded render/write scheduler limits."""

    max_render_workers: int = 2
    max_pending_files: int = 8
    max_pending_bytes: int = 16 * 1024 * 1024
    wait_timeout_seconds: float = 0.05


@dataclass(frozen=True, slots=True)
class GraphQueueStats:
    """Observed queue pressure for one graph emission."""

    pending_files_high_water: int = 0
    pending_bytes_high_water: int = 0
    queue_waits: int = 0
    files_written: int = 0


@dataclass(frozen=True, slots=True)
class RenderedGraphFile:
    """One rendered or raw file ready for the single writer."""

    file: EmissionFile
    content: str | bytes | None
    estimated_bytes: int
    immutable_existing: bool = False


@dataclass(frozen=True, slots=True)
class GraphWriteCompletion:
    """One writer completion consumed by the dependency scheduler."""

    item: RenderedGraphFile
    result: EmissionWriteResult


@dataclass(slots=True)
class _MutableStats:
    pending_files_high_water: int = 0
    pending_bytes_high_water: int = 0
    queue_waits: int = 0
    files_written: int = 0

    def snapshot(self) -> GraphQueueStats:
        return GraphQueueStats(
            pending_files_high_water=self.pending_files_high_water,
            pending_bytes_high_water=self.pending_bytes_high_water,
            queue_waits=self.queue_waits,
            files_written=self.files_written,
        )


class _FailureState:
    def __init__(self) -> None:
        self._lock = Lock()
        self._error: BaseException | None = None

    def set(self, error: BaseException) -> None:
        with self._lock:
            if self._error is None:
                self._error = error

    def get(self) -> BaseException | None:
        with self._lock:
            return self._error

    def raise_if_failed(self) -> None:
        error = self.get()
        if error is not None:
            raise GraphQueueError("Generated-file writer failed") from error


class GraphWriteQueue:
    """One byte-bounded ordered writer for generated files."""

    def __init__(
        self,
        *,
        limits: GraphQueueLimits | None = None,
        on_queued: Callable[[EmissionFile], None] | None = None,
    ) -> None:
        self.limits = limits or GraphQueueLimits()
        _validate_limits(self.limits)
        self._on_queued = on_queued
        self._queue: Queue[RenderedGraphFile | object] = Queue(
            maxsize=self.limits.max_pending_files
        )
        self._completions: Queue[GraphWriteCompletion] = Queue()
        self._condition = Condition()
        self._pending_bytes = 0
        self._failure = _FailureState()
        self._stats = _MutableStats()
        self._closed = False
        self._thread = Thread(
            target=self._run,
            name="codepotg-generated-writer",
            daemon=True,
        )

    def start(self) -> None:
        self._thread.start()

    def submit(self, item: RenderedGraphFile) -> None:
        if self._closed:
            raise GraphQueueError("Generated-file writer is already closed")
        size = max(1, item.estimated_bytes)
        self._reserve_bytes(size)
        try:
            self._put(item)
        except BaseException:
            self._release_bytes(size)
            raise
        if self._on_queued is not None:
            self._on_queued(item.file)

    def completion(self, *, block: bool = False) -> GraphWriteCompletion | None:
        self._failure.raise_if_failed()
        try:
            return self._completions.get(
                block=block,
                timeout=self.limits.wait_timeout_seconds if block else None,
            )
        except Empty:
            return None

    def close(self) -> GraphQueueStats:
        if not self._closed:
            self._put(_SENTINEL, ignore_failure=True)
            self._queue.join()
            self._thread.join()
            self._closed = True
        self._failure.raise_if_failed()
        return self._stats.snapshot()

    def _put(
        self,
        item: RenderedGraphFile | object,
        *,
        ignore_failure: bool = False,
    ) -> None:
        while True:
            if not ignore_failure:
                self._failure.raise_if_failed()
            try:
                self._queue.put(item, timeout=self.limits.wait_timeout_seconds)
                self._stats.pending_files_high_water = max(
                    self._stats.pending_files_high_water,
                    self._queue.qsize(),
                )
                return
            except Full:
                self._stats.queue_waits += 1

    def _reserve_bytes(self, size: int) -> None:
        with self._condition:
            while True:
                self._failure.raise_if_failed()
                oversized = size > self.limits.max_pending_bytes
                has_capacity = (
                    self._pending_bytes == 0
                    if oversized
                    else self._pending_bytes + size <= self.limits.max_pending_bytes
                )
                if has_capacity:
                    self._pending_bytes += size
                    self._stats.pending_bytes_high_water = max(
                        self._stats.pending_bytes_high_water,
                        self._pending_bytes,
                    )
                    return
                self._stats.queue_waits += 1
                self._condition.wait(self.limits.wait_timeout_seconds)

    def _release_bytes(self, size: int) -> None:
        with self._condition:
            self._pending_bytes = max(0, self._pending_bytes - size)
            self._condition.notify_all()

    def _run(self) -> None:
        try:
            while True:
                item = self._queue.get()
                try:
                    if item is _SENTINEL:
                        return
                    if not isinstance(item, RenderedGraphFile):
                        raise TypeError("Generated-file queue received an invalid item")
                    result = _write(item)
                    self._stats.files_written += 1
                    self._completions.put(GraphWriteCompletion(item=item, result=result))
                finally:
                    if isinstance(item, RenderedGraphFile):
                        self._release_bytes(max(1, item.estimated_bytes))
                    self._queue.task_done()
        except BaseException as exc:
            self._failure.set(exc)
            self._drain_after_failure()

    def _drain_after_failure(self) -> None:
        while True:
            item = self._queue.get()
            if isinstance(item, RenderedGraphFile):
                self._release_bytes(max(1, item.estimated_bytes))
            self._queue.task_done()
            if item is _SENTINEL:
                return


def rendered_size(content: str | bytes | None) -> int:
    """Return the byte estimate used for write-queue backpressure."""

    if isinstance(content, str):
        return len(content.encode("utf-8"))
    if isinstance(content, bytes):
        return len(content)
    return 1


def _write(item: RenderedGraphFile) -> EmissionWriteResult:
    file = item.file
    if item.immutable_existing:
        return EmissionWriteResult(
            skipped=(file.output_path,),
            immutable_skipped=(file.output_path,),
        )
    if file.is_template:
        if not isinstance(item.content, str):
            raise TypeError(f"Rendered template content must be text: {file.template_path}")
        result = write_text_if_changed(
            file.output_path,
            item.content,
            compare_mode=file.compare_mode,
        )
    else:
        if not isinstance(item.content, bytes):
            raise TypeError(f"Raw template content must be bytes: {file.template_path}")
        result = write_bytes_if_changed(file.output_path, item.content)
    if file.lifecycle == PathLifecycleMode.IMMUTABLE and result.created:
        return EmissionWriteResult(
            created=result.created,
            immutable_created=result.created,
        )
    return result


def _validate_limits(limits: GraphQueueLimits) -> None:
    if limits.max_render_workers < 1:
        raise ValueError("max_render_workers must be at least 1")
    if limits.max_pending_files < 1:
        raise ValueError("max_pending_files must be at least 1")
    if limits.max_pending_bytes < 1:
        raise ValueError("max_pending_bytes must be at least 1")
    if limits.wait_timeout_seconds <= 0:
        raise ValueError("wait_timeout_seconds must be greater than 0")
