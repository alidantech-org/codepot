from __future__ import annotations

from pathlib import Path
from threading import Event

import pytest

from contracts.emission import EmissionFile
from archives.codepotg.tests.emission import graph_queue
from emission.graph_queue import (
    GraphQueueError,
    GraphQueueLimits,
    GraphWriteQueue,
    RenderedGraphFile,
)


def test_graph_write_queue_applies_file_and_byte_bounds(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entered = Event()
    release = Event()
    original = graph_queue._write

    def blocking_write(item: RenderedGraphFile):
        entered.set()
        release.wait(timeout=5)
        return original(item)

    monkeypatch.setattr(graph_queue, "_write", blocking_write)
    queue = GraphWriteQueue(
        limits=GraphQueueLimits(
            max_render_workers=1,
            max_write_workers=1,
            max_pending_files=1,
            max_pending_bytes=4,
            wait_timeout_seconds=0.01,
        )
    )
    queue.start()
    first = _item(tmp_path / "first.txt", "first")
    queue.submit(first)
    assert entered.wait(timeout=2)

    release.set()
    completion = queue.completion(block=True)
    assert completion is not None
    stats = queue.close()

    assert completion.result.created == (tmp_path / "first.txt",)
    assert stats.pending_files_high_water <= 1
    assert stats.pending_bytes_high_water == len(b"first")
    assert stats.files_written == 1
    assert stats.batches_written == 1


def test_graph_write_queue_batches_multiple_files(tmp_path: Path) -> None:
    queue = GraphWriteQueue(
        limits=GraphQueueLimits(
            max_render_workers=2,
            max_write_workers=3,
            max_pending_files=8,
            max_pending_bytes=1024,
            write_batch_files=3,
            write_batch_bytes=1024,
        )
    )
    items = tuple(
        _item(tmp_path / f"file-{index}.txt", f"value-{index}")
        for index in range(6)
    )

    # Fill the bounded queue before starting the worker so batching is deterministic.
    for item in items:
        queue.submit(item)
    queue.start()

    completions = tuple(queue.completion(block=True) for _ in items)
    stats = queue.close()

    assert all(completion is not None for completion in completions)
    assert {path.name for path in tmp_path.glob("*.txt")} == {
        f"file-{index}.txt" for index in range(6)
    }
    assert stats.files_written == 6
    assert stats.batches_written == 2
    assert stats.batch_files_high_water == 3
    assert stats.batch_bytes_high_water > 1


def test_graph_write_queue_allows_one_oversized_item_when_empty(tmp_path: Path) -> None:
    queue = GraphWriteQueue(
        limits=GraphQueueLimits(
            max_render_workers=1,
            max_pending_files=1,
            max_pending_bytes=2,
        )
    )
    queue.start()
    queue.submit(_item(tmp_path / "large.txt", "larger"))

    completion = queue.completion(block=True)
    stats = queue.close()

    assert completion is not None
    assert completion.result.created == (tmp_path / "large.txt",)
    assert stats.pending_bytes_high_water == len(b"larger")


def test_graph_write_queue_propagates_writer_failure_without_hanging(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = graph_queue._write

    def fail_one_write(item: RenderedGraphFile):
        if item.file.output_path.name == "failed.txt":
            raise OSError(f"cannot write {item.file.output_path}")
        return original(item)

    monkeypatch.setattr(graph_queue, "_write", fail_one_write)
    queue = GraphWriteQueue(
        limits=GraphQueueLimits(
            max_render_workers=1,
            max_write_workers=2,
            max_pending_files=4,
            write_batch_files=4,
        )
    )
    queue.submit(_item(tmp_path / "failed.txt", "failed"))
    queue.submit(_item(tmp_path / "completed.txt", "completed"))
    queue.start()

    with pytest.raises(GraphQueueError, match="writer failed"):
        queue.close()

    assert not (tmp_path / "failed.txt").exists()
    assert (tmp_path / "completed.txt").read_text(encoding="utf-8") == "completed\n"


def _item(path: Path, content: str) -> RenderedGraphFile:
    return RenderedGraphFile(
        file=EmissionFile(
            template_path=Path("file.txt.j2"),
            output_path=path,
            context={},
        ),
        content=content,
        estimated_bytes=len(content.encode("utf-8")),
    )
