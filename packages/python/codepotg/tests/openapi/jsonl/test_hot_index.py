from __future__ import annotations

from openapi.jsonl import BoundedHotIndex, HotIndexLimits


def test_hot_index_enforces_lru_entry_and_byte_limits() -> None:
    index: BoundedHotIndex[str] = BoundedHotIndex(
        HotIndexLimits(max_entries=2, max_bytes=128),
        estimate=lambda key, value: len(key) + len(value),
    )

    assert index.put("first", "1" * 20)
    assert index.put("second", "2" * 20)
    assert index.get("first") == "1" * 20
    assert index.put("third", "3" * 20)

    assert index.get("second") is None
    assert index.get("first") == "1" * 20
    assert index.get("third") == "3" * 20

    stats = index.stats()
    assert stats.entries == 2
    assert stats.estimated_bytes <= 128
    assert stats.evictions == 1
    assert stats.hits == 3
    assert stats.misses == 1


def test_hot_index_rejects_one_value_larger_than_total_budget() -> None:
    index: BoundedHotIndex[str] = BoundedHotIndex(
        HotIndexLimits(max_entries=2, max_bytes=16),
        estimate=lambda key, value: len(key) + len(value),
    )

    assert not index.put("oversized", "x" * 32)
    assert len(index) == 0
