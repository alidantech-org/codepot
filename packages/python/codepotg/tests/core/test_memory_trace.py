from __future__ import annotations

import json

from core.memory_trace import MemoryTrace


def test_disabled_memory_trace_has_no_snapshots() -> None:
    trace = MemoryTrace(enabled=False)

    assert trace.snapshot("disabled") is None
    assert trace.summaries() == ()


def test_memory_trace_records_stage_and_jsonl(tmp_path) -> None:
    output = tmp_path / "memory.jsonl"
    trace = MemoryTrace(
        enabled=True,
        trace_allocations=True,
        output_path=output,
    )
    try:
        snapshot = trace.snapshot("unit")
    finally:
        trace.close()

    assert snapshot is not None
    assert snapshot.stage == "unit"
    assert snapshot.elapsed_ms >= 0
    assert snapshot.python_bytes is not None
    assert snapshot.python_peak_bytes is not None
    assert trace.summaries()[0].startswith("Memory trace: stage=unit")

    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    assert rows[0]["stage"] == "unit"
    assert rows[0]["python_bytes"] is not None
