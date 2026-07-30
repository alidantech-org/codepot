from __future__ import annotations

from core import system_resources
from core.system_resources import SystemResources, detect_system_resources, tune_runtime


def test_detect_system_resources_has_positive_cpu_count() -> None:
    resources = detect_system_resources()

    assert resources.cpu_count >= 1
    if resources.total_memory is not None:
        assert resources.total_memory > 0
    if resources.available_memory is not None:
        assert resources.available_memory > 0


def test_runtime_tuning_uses_available_memory_without_claiming_it_all(
    monkeypatch,
) -> None:
    available = 8 * 1024 * 1024 * 1024
    monkeypatch.setattr(
        system_resources,
        "detect_system_resources",
        lambda: SystemResources(
            cpu_count=16,
            total_memory=16 * 1024 * 1024 * 1024,
            available_memory=available,
        ),
    )

    tuning = tune_runtime(32 * 1024 * 1024, planned_files=1_000)

    assert tuning.available_memory == available
    assert tuning.render_workers == 12
    assert tuning.write_workers == 8
    assert 16 <= tuning.pending_files <= 256
    assert 64 <= tuning.jsonl_pending_records <= 2_048
    assert tuning.jsonl_pending_bytes <= available // 4
    assert tuning.pending_render_bytes <= available // 4
    assert tuning.sqlite_cache_bytes <= available // 4
    assert tuning.write_batch_files == 64
    assert tuning.write_batch_bytes <= 32 * 1024 * 1024
    assert "available=8.0GiB" in tuning.summary()


def test_runtime_tuning_keeps_low_memory_hosts_bounded(monkeypatch) -> None:
    monkeypatch.setattr(
        system_resources,
        "detect_system_resources",
        lambda: SystemResources(
            cpu_count=2,
            total_memory=512 * 1024 * 1024,
            available_memory=192 * 1024 * 1024,
        ),
    )

    tuning = tune_runtime(256 * 1024 * 1024, planned_files=10_000)

    assert tuning.render_workers == 2
    assert tuning.write_workers == 2
    assert tuning.pending_files <= 256
    assert tuning.hot_index_bytes <= 256 * 1024 * 1024
    assert tuning.sqlite_cache_bytes <= 512 * 1024 * 1024
    assert tuning.jsonl_pending_bytes <= 128 * 1024 * 1024
