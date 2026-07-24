from __future__ import annotations

from pathlib import Path
from threading import Event

import pytest

from contracts.emission import EmissionFile
from emission import graph_queue
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


def test_graph_write_queue_propagates_writer_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_write(item: RenderedGraphFile):
        raise OSError(f"cannot write {item.file.output_path}")

    monkeypatch.setattr(graph_queue, "_write", fail_write)
    queue = GraphWriteQueue(
        limits=GraphQueueLimits(max_render_workers=1, max_pending_files=1)
    )
    queue.start()
    queue.submit(_item(tmp_path / "failed.txt", "failed"))

    with pytest.raises(GraphQueueError, match="writer failed"):
        queue.close()

    assert not (tmp_path / "failed.txt").exists()


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
