from __future__ import annotations

import json
from pathlib import Path
from threading import Event, Thread

import pytest

from openapi.jsonl import JsonlQueueError, JsonlQueueLimits
from openapi.jsonl.models import ExtractedRecord
from openapi.jsonl.queueing import JsonlRecordPipeline, create_event_writer_factory


def test_record_pipeline_blocks_on_pending_byte_limit(tmp_path: Path) -> None:
    entered = Event()
    release = Event()
    producer_started = Event()
    submitted = Event()
    processed: list[str] = []

    def process(record: ExtractedRecord) -> None:
        entered.set()
        assert release.wait(2)
        processed.append(record.name)

    pipeline = JsonlRecordPipeline(
        process,
        limits=JsonlQueueLimits(
            max_records=2,
            max_pending_bytes=10,
            max_events=2,
            wait_timeout_seconds=0.01,
        ),
        event_writer_factory=create_event_writer_factory(tmp_path),
    )
    pipeline.start()
    pipeline.submit(
        ExtractedRecord(section="components/schemas", name="First", raw={}, estimated_bytes=6)
    )
    assert entered.wait(1)

    def submit_second() -> None:
        producer_started.set()
        pipeline.submit(
            ExtractedRecord(
                section="components/schemas",
                name="Second",
                raw={},
                estimated_bytes=6,
            )
        )
        submitted.set()

    producer = Thread(target=submit_second)
    producer.start()
    assert producer_started.wait(1)
    assert not submitted.wait(0.05)

    release.set()
    assert submitted.wait(1)
    producer.join(1)
    assert not producer.is_alive()

    event_manifest, stats = pipeline.close()

    assert processed == ["First", "Second"]
    assert stats.record_high_water <= 2
    assert stats.pending_bytes_high_water <= 10
    assert stats.event_high_water <= 2
    assert stats.record_waits > 0

    events = [
        json.loads(line)
        for line in (tmp_path / event_manifest.file).read_text().splitlines()
    ]
    assert event_manifest.count == 6
    assert events[0]["status"] == "started"
    assert events[-1]["status"] == "completed"


def test_record_pipeline_propagates_writer_failure(tmp_path: Path) -> None:
    def fail(record: ExtractedRecord) -> None:
        raise RuntimeError(f"cannot write {record.name}")

    pipeline = JsonlRecordPipeline(
        fail,
        limits=JsonlQueueLimits(
            max_records=1,
            max_pending_bytes=1024,
            max_events=1,
            wait_timeout_seconds=0.01,
        ),
        event_writer_factory=create_event_writer_factory(tmp_path),
    )
    pipeline.start()
    pipeline.submit(
        ExtractedRecord(section="components/schemas", name="Broken", raw={})
    )

    with pytest.raises(JsonlQueueError, match="worker failed") as raised:
        pipeline.close()

    assert isinstance(raised.value.__cause__, RuntimeError)
