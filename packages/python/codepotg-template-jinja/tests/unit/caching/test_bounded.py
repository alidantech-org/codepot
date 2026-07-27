from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from codepotg_template_jinja.caching import BoundedCache


def test_cache_tracks_hits_misses_and_eviction() -> None:
    cache: BoundedCache[str] = BoundedCache(2)
    assert cache.get("missing") is None
    cache.put("a", "A")
    cache.put("b", "B")
    assert cache.get("a") == "A"
    cache.put("c", "C")
    assert cache.get("b") is None
    stats = cache.stats()
    assert stats.entries == 2
    assert stats.hits == 1
    assert stats.evictions == 1


def test_clear_removes_entries() -> None:
    cache: BoundedCache[int] = BoundedCache(1)
    cache.put("x", 1)
    cache.clear()
    assert cache.stats().entries == 0


def test_concurrent_access_remains_bounded() -> None:
    cache: BoundedCache[int] = BoundedCache(8)

    def work(index: int) -> None:
        key = str(index % 16)
        cache.put(key, index)
        cache.get(key)

    with ThreadPoolExecutor(max_workers=8) as executor:
        tuple(executor.map(work, range(2_000)))
    assert cache.stats().entries <= 8
