from __future__ import annotations

import hashlib
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from queue import Full, Queue
from threading import Condition, Lock, Thread
from typing import Any

from .errors import JsonlQueueError
from .indexing import canonical_json_bytes
from .models import ExtractedRecord, JsonlQueueLimits, JsonlQueueStats, SectionManifest

_SENTINEL = object()


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
        if error is None:
            return
        raise JsonlQueueError("A JSONL pipeline worker failed") from error


@dataclass(slots=True)
class _MutableQueueStats:
    record_high_water: int = 0
    pending_bytes_high_water: int = 0
    event_high_water: int = 0
    record_waits: int = 0
    event_waits: int = 0

    def snapshot(self) -> JsonlQueueStats:
        return JsonlQueueStats(
            record_high_water=self.record_high_water,
            pending_bytes_high_water=self.pending_bytes_high_water,
            event_high_water=self.event_high_water,
            record_waits=self.record_waits,
            event_waits=self.event_waits,
        )


class JsonlEventWriter:
    """One ordered writer for deterministic compiler events."""

    def __init__(
        self,
        root: Path,
        *,
        limits: JsonlQueueLimits,
        failure: _FailureState,
        stats: _MutableQueueStats,
    ) -> None:
        self._path = root / "events.jsonl"
        self._limits = limits
        self._failure = failure
        self._stats = stats
        self._queue: Queue[Mapping[str, Any] | object] = Queue(maxsize=limits.max_events)
        self._thread = Thread(target=self._run, name="codepotg-jsonl-events", daemon=True)
        self._manifest: SectionManifest | None = None
        self._closed = False

    def start(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._thread.start()

    def submit(self, stage: str, status: str, **details: Any) -> None:
        if self._closed:
            raise JsonlQueueError("JSONL event writer is already closed")
        event = {"stage": stage, "status": status, **details}
        self._put(event)

    def close(self) -> SectionManifest:
        if not self._closed:
            self._put(_SENTINEL, ignore_failure=True)
            self._queue.join()
            self._thread.join()
            self._closed = True
        self._failure.raise_if_failed()
        if self._manifest is None:
            raise JsonlQueueError("JSONL event writer did not produce a manifest")
        return self._manifest

    def _put(self, item: Mapping[str, Any] | object, *, ignore_failure: bool = False) -> None:
        while True:
            if not ignore_failure:
                self._failure.raise_if_failed()
            try:
                self._queue.put(item, timeout=self._limits.wait_timeout_seconds)
                self._stats.event_high_water = max(
                    self._stats.event_high_water,
                    self._queue.qsize(),
                )
                return
            except Full:
                self._stats.event_waits += 1

    def _run(self) -> None:
        hasher = hashlib.sha256()
        count = 0
        byte_count = 0
        sequence = 0
        try:
            with self._path.open("wb") as stream:
                while True:
                    item = self._queue.get()
                    try:
                        if item is _SENTINEL:
                            break
                        if not isinstance(item, Mapping):
                            raise TypeError("JSONL event queue received an invalid item")
                        sequence += 1
                        line = canonical_json_bytes({"sequence": sequence, **item}) + b"\n"
                        stream.write(line)
                        hasher.update(line)
                        count += 1
                        byte_count += len(line)
                    finally:
                        self._queue.task_done()
            self._manifest = SectionManifest(
                file="events.jsonl",
                count=count,
                bytes=byte_count,
                sha256=f"sha256:{hasher.hexdigest()}",
            )
        except BaseException as exc:
            self._failure.set(exc)
            self._drain_after_failure()

    def _drain_after_failure(self) -> None:
        while True:
            item = self._queue.get()
            self._queue.task_done()
            if item is _SENTINEL:
                return


class JsonlRecordPipeline:
    """Bounded parser-to-writer queue with byte-aware backpressure."""

    def __init__(
        self,
        process: Callable[[ExtractedRecord], None],
        *,
        limits: JsonlQueueLimits | None = None,
        event_writer_factory: Callable[
            [JsonlQueueLimits, _FailureState, _MutableQueueStats], JsonlEventWriter
        ],
    ) -> None:
        self._limits = limits or JsonlQueueLimits()
        _validate_limits(self._limits)
        self._process = process
        self._failure = _FailureState()
        self._stats = _MutableQueueStats()
        self._queue: Queue[ExtractedRecord | object] = Queue(
            maxsize=self._limits.max_records
        )
        self._bytes_condition = Condition()
        self._pending_bytes = 0
        self._cancelled = False
        self._closed = False
        self._event_writer = event_writer_factory(
            self._limits,
            self._failure,
            self._stats,
        )
        self._thread = Thread(target=self._run, name="codepotg-jsonl-writer", daemon=True)

    def start(self) -> None:
        self._event_writer.start()
        self._event_writer.submit("compiler", "started")
        self._thread.start()

    def submit(self, record: ExtractedRecord) -> None:
        if self._closed:
            raise JsonlQueueError("JSONL record pipeline is already closed")
        size = max(1, record.estimated_bytes)
        self._reserve_bytes(size)
        try:
            self._put_record(record)
        except BaseException:
            self._release_bytes(size)
            raise

    def cancel(self) -> None:
        self._cancelled = True
        with self._bytes_condition:
            self._bytes_condition.notify_all()

    def close(self) -> tuple[SectionManifest, JsonlQueueStats]:
        if not self._closed:
            self._put_record(_SENTINEL, ignore_failure=True)
            self._queue.join()
            self._thread.join()
            if self._failure.get() is None:
                status = "cancelled" if self._cancelled else "completed"
                self._event_writer.submit("compiler", status)
            try:
                event_manifest = self._event_writer.close()
            finally:
                self._closed = True
            self._failure.raise_if_failed()
            return event_manifest, self._stats.snapshot()
        self._failure.raise_if_failed()
        event_manifest = self._event_writer.close()
        return event_manifest, self._stats.snapshot()

    def _put_record(
        self,
        item: ExtractedRecord | object,
        *,
        ignore_failure: bool = False,
    ) -> None:
        while True:
            if not ignore_failure:
                self._failure.raise_if_failed()
            try:
                self._queue.put(item, timeout=self._limits.wait_timeout_seconds)
                self._stats.record_high_water = max(
                    self._stats.record_high_water,
                    self._queue.qsize(),
                )
                return
            except Full:
                self._stats.record_waits += 1

    def _reserve_bytes(self, size: int) -> None:
        with self._bytes_condition:
            while True:
                self._failure.raise_if_failed()
                if self._cancelled:
                    raise JsonlQueueError("JSONL record pipeline was cancelled")
                oversized = size > self._limits.max_pending_bytes
                has_capacity = (
                    self._pending_bytes == 0
                    if oversized
                    else self._pending_bytes + size <= self._limits.max_pending_bytes
                )
                if has_capacity:
                    self._pending_bytes += size
                    self._stats.pending_bytes_high_water = max(
                        self._stats.pending_bytes_high_water,
                        self._pending_bytes,
                    )
                    return
                self._stats.record_waits += 1
                self._bytes_condition.wait(self._limits.wait_timeout_seconds)

    def _release_bytes(self, size: int) -> None:
        with self._bytes_condition:
            self._pending_bytes = max(0, self._pending_bytes - size)
            self._bytes_condition.notify_all()

    def _run(self) -> None:
        try:
            while True:
                item = self._queue.get()
                try:
                    if item is _SENTINEL:
                        return
                    if not isinstance(item, ExtractedRecord):
                        raise TypeError("JSONL record queue received an invalid item")
                    if self._cancelled or self._failure.get() is not None:
                        continue
                    if self._limits.emit_record_events:
                        self._event_writer.submit(
                            "record",
                            "started",
                            section=item.section,
                            name=item.name,
                        )
                    self._process(item)
                    if self._limits.emit_record_events:
                        self._event_writer.submit(
                            "record",
                            "written",
                            section=item.section,
                            name=item.name,
                        )
                finally:
                    if isinstance(item, ExtractedRecord):
                        self._release_bytes(max(1, item.estimated_bytes))
                    self._queue.task_done()
        except BaseException as exc:
            self._failure.set(exc)
            self._drain_after_failure()

    def _drain_after_failure(self) -> None:
        while True:
            item = self._queue.get()
            if isinstance(item, ExtractedRecord):
                self._release_bytes(max(1, item.estimated_bytes))
            self._queue.task_done()
            if item is _SENTINEL:
                return


def create_event_writer_factory(
    root: Path,
) -> Callable[[JsonlQueueLimits, _FailureState, _MutableQueueStats], JsonlEventWriter]:
    def factory(
        limits: JsonlQueueLimits,
        failure: _FailureState,
        stats: _MutableQueueStats,
    ) -> JsonlEventWriter:
        return JsonlEventWriter(root, limits=limits, failure=failure, stats=stats)

    return factory


def _validate_limits(limits: JsonlQueueLimits) -> None:
    if limits.max_records < 1:
        raise ValueError("max_records must be at least 1")
    if limits.max_pending_bytes < 1:
        raise ValueError("max_pending_bytes must be at least 1")
    if limits.max_events < 1:
        raise ValueError("max_events must be at least 1")
    if limits.wait_timeout_seconds <= 0:
        raise ValueError("wait_timeout_seconds must be greater than 0")
