from __future__ import annotations

from dryv.features.cache import (
    CacheEntry,
    CacheFeature,
    CacheMode,
    CacheStage,
    ContextCacheKey,
    RenderCacheKey,
    cache_entry_bytes,
)


def _context_key(hash_value: str = "hash:a") -> ContextCacheKey:
    return ContextCacheKey((("schema.a", hash_value),), 1, "pack:1", "inputs:1")


def test_use_mode_reads_committed_entries() -> None:
    feature = CacheFeature()
    key = _context_key()
    tx = feature.begin(CacheMode.USE)
    tx.put(CacheEntry(CacheStage.CONTEXT, key, b"context"))
    tx.commit()
    reader = feature.begin(CacheMode.USE)
    assert reader.get(CacheStage.CONTEXT, key).payload == b"context"  # type: ignore[union-attr]


def test_refresh_ignores_old_entries_but_can_replace_them() -> None:
    feature = CacheFeature()
    key = _context_key()
    first = feature.begin(CacheMode.USE)
    first.put(CacheEntry(CacheStage.CONTEXT, key, b"old"))
    first.commit()

    refresh = feature.begin(CacheMode.REFRESH)
    assert refresh.get(CacheStage.CONTEXT, key) is None
    refresh.put(CacheEntry(CacheStage.CONTEXT, key, b"new"))
    refresh.commit()

    assert feature.begin(CacheMode.USE).get(CacheStage.CONTEXT, key).payload == b"new"  # type: ignore[union-attr]


def test_off_and_non_committing_plan_do_not_mutate_storage() -> None:
    feature = CacheFeature()
    key = _context_key()
    for mode, commit_enabled in ((CacheMode.OFF, True), (CacheMode.USE, False)):
        tx = feature.begin(mode, commit_enabled=commit_enabled)
        tx.put(CacheEntry(CacheStage.CONTEXT, key, b"ignored"))
        tx.commit()
    assert feature.begin(CacheMode.USE).get(CacheStage.CONTEXT, key) is None


def test_failed_work_rolls_back_without_poisoning_prior_cache() -> None:
    feature = CacheFeature()
    key = _context_key()
    valid = feature.begin(CacheMode.USE)
    valid.put(CacheEntry(CacheStage.CONTEXT, key, b"valid"))
    valid.commit()

    failed = feature.begin(CacheMode.USE)
    failed.put(CacheEntry(CacheStage.CONTEXT, key, b"bad"))
    failed.rollback()
    assert feature.begin(CacheMode.USE).get(CacheStage.CONTEXT, key).payload == b"valid"  # type: ignore[union-attr]


def test_renderer_fingerprint_is_part_of_render_cache_identity() -> None:
    first = RenderCacheKey("context", "template", "renderer:v1", "options", 1, 1)
    second = RenderCacheKey("context", "template", "renderer:v2", "options", 1, 1)
    assert first != second


def test_cache_serialization_is_deterministic() -> None:
    entry = CacheEntry(CacheStage.CONTEXT, _context_key(), b"context", (("source", "test"),))
    assert cache_entry_bytes(entry) == cache_entry_bytes(entry)
    assert b'"stage":"context"' in cache_entry_bytes(entry)
