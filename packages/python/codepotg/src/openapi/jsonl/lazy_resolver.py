from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .errors import JsonlLookupError
from .models import HotIndexLimits, RecordLocation
from .selections import JsonlSelectionStore
from .store import JsonlIndexStore


@dataclass(frozen=True, slots=True)
class LazyResolverLimits:
    """Bounds for one template resolver instance."""

    max_depth: int = 32
    max_related_items: int = 10_000
    max_record_bytes: int = 16 * 1024 * 1024
    cache_entries: int = 256
    cache_bytes: int = 32 * 1024 * 1024


class LazyJsonlRecord(Mapping[str, Any]):
    """Mapping proxy that loads one indexed raw record on first access."""

    def __init__(
        self,
        *,
        location: RecordLocation,
        loader: Callable[[RecordLocation], Any],
    ) -> None:
        self.location = location
        self._loader = loader
        self._loaded = False
        self._raw: Mapping[str, Any] | None = None

    @property
    def key(self) -> str:
        return self.location.key

    @property
    def ref(self) -> str | None:
        return self.location.ref

    @property
    def kind(self) -> str | None:
        return self.location.kind

    @property
    def resources(self) -> tuple[str, ...]:
        return self.location.resources

    @property
    def loaded(self) -> bool:
        return self._loaded

    @property
    def raw(self) -> Mapping[str, Any]:
        return self._value()

    def __getitem__(self, key: str) -> Any:
        return self._value()[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._value())

    def __len__(self) -> int:
        return len(self._value())

    def get(self, key: str, default: Any = None) -> Any:
        return self._value().get(key, default)

    def _value(self) -> Mapping[str, Any]:
        if self._raw is None:
            raw = self._loader(self.location)
            if not isinstance(raw, Mapping):
                raise JsonlLookupError(
                    f"Lazy JSONL record is not an object: {self.location.key}"
                )
            self._raw = raw
            self._loaded = True
        return self._raw


class JsonlLazyResolver:
    """Template-safe lazy resolver backed by JSONL indexes and bounded caches."""

    def __init__(
        self,
        cache_dir: str | Path,
        *,
        limits: LazyResolverLimits | None = None,
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.limits = limits or LazyResolverLimits()
        _validate_limits(self.limits)
        hot_limits = HotIndexLimits(
            max_entries=self.limits.cache_entries,
            max_bytes=self.limits.cache_bytes,
        )
        self.index_store = JsonlIndexStore(self.cache_dir)
        self.selection_store = JsonlSelectionStore(
            self.cache_dir,
            raw_cache_limits=hot_limits,
            index_store=self.index_store,
        )
        self._proxies: dict[str, LazyJsonlRecord] = {}
        self._load_count = 0

    @property
    def load_count(self) -> int:
        return self._load_count

    def ref(self, ref: str) -> LazyJsonlRecord | None:
        """Return a lazy proxy for a canonical ref."""

        location = self.index_store.get_by_ref(ref)
        return self._proxy(location)

    def key(self, key: str) -> LazyJsonlRecord | None:
        """Return a lazy proxy for a stable source key."""

        location = self.index_store.get_by_key(key)
        return self._proxy(location)

    def operation(self, operation_id: str) -> LazyJsonlRecord | None:
        """Return a lazy operation proxy by operationId."""

        location = self.index_store.get_by_operation_id(operation_id)
        return self._proxy(location)

    def resource(self, resource: str) -> tuple[LazyJsonlRecord, ...]:
        """Return lazy records declaring or mentioning one resource."""

        facts = self.index_store.find_mentions("resource", resource)
        return self._facts_to_proxies(facts)

    def mentions(self, index: str, value: str) -> tuple[LazyJsonlRecord, ...]:
        """Return records found through one mention index."""

        return self._facts_to_proxies(self.index_store.find_mentions(index, value))

    def dependants(self, ref: str) -> tuple[LazyJsonlRecord, ...]:
        """Return lazy records that directly depend on a ref."""

        return self._facts_to_proxies(
            self.index_store.find_dependants(ref),
            item_field="from",
        )

    def chain(self, ref: str, *, depth: int = 1) -> tuple[LazyJsonlRecord, ...]:
        """Resolve a bounded breadth-first dependency chain lazily."""

        if depth < 0 or depth > self.limits.max_depth:
            raise JsonlLookupError(
                f"Lazy resolver depth {depth} exceeds limit {self.limits.max_depth}"
            )
        result: list[LazyJsonlRecord] = []
        seen_refs: set[str] = set()
        frontier = [ref]
        for _ in range(depth + 1):
            next_frontier: list[str] = []
            for current in frontier:
                if current in seen_refs:
                    continue
                seen_refs.add(current)
                proxy = self.ref(current)
                if proxy is not None:
                    result.append(proxy)
                for fact in self.index_store.find_dependants(current):
                    source = fact.get("from")
                    if not isinstance(source, str):
                        continue
                    source_proxy = self.key(source)
                    if source_proxy is not None and source_proxy.ref:
                        next_frontier.append(source_proxy.ref)
                if len(result) + len(next_frontier) > self.limits.max_related_items:
                    raise JsonlLookupError(
                        "Lazy resolver related-item limit exceeded: "
                        f"{self.limits.max_related_items}"
                    )
            frontier = next_frontier
            if not frontier:
                break
        return tuple(_unique_proxies(result))

    def stats(self) -> dict[str, Any]:
        """Return bounded resolver and source-load diagnostics."""

        return {
            "loads": self._load_count,
            "proxies": len(self._proxies),
            "rawCache": self.selection_store.raw_cache_stats(),
        }

    def _proxy(self, location: RecordLocation | None) -> LazyJsonlRecord | None:
        if location is None:
            return None
        if location.length > self.limits.max_record_bytes:
            raise JsonlLookupError(
                f"Indexed record exceeds lazy resolver byte limit: {location.key}"
            )
        pointer = location.pointer or ""
        identity = f"{location.file}:{location.offset}:{location.length}:{pointer}"
        proxy = self._proxies.get(identity)
        if proxy is None:
            if len(self._proxies) >= self.limits.cache_entries:
                oldest = next(iter(self._proxies))
                self._proxies.pop(oldest)
            proxy = LazyJsonlRecord(location=location, loader=self._load)
            self._proxies[identity] = proxy
        return proxy

    def _load(self, location: RecordLocation) -> Any:
        self._load_count += 1
        return self.index_store.read_location(location)

    def _facts_to_proxies(
        self,
        facts: tuple[Mapping[str, Any], ...],
        *,
        item_field: str = "item",
    ) -> tuple[LazyJsonlRecord, ...]:
        proxies: list[LazyJsonlRecord] = []
        for fact in facts:
            item = fact.get(item_field)
            if not isinstance(item, str):
                continue
            proxy = self.key(item)
            if proxy is not None:
                proxies.append(proxy)
            if len(proxies) > self.limits.max_related_items:
                raise JsonlLookupError(
                    "Lazy resolver related-item limit exceeded: "
                    f"{self.limits.max_related_items}"
                )
        return tuple(_unique_proxies(proxies))


def _unique_proxies(values: list[LazyJsonlRecord]) -> Iterator[LazyJsonlRecord]:
    seen: set[str] = set()
    for value in values:
        identity = (
            f"{value.location.file}:{value.location.offset}:"
            f"{value.location.length}:{value.location.pointer or ''}"
        )
        if identity in seen:
            continue
        seen.add(identity)
        yield value


def _validate_limits(limits: LazyResolverLimits) -> None:
    if limits.max_depth < 0:
        raise ValueError("max_depth must be non-negative")
    if limits.max_related_items < 1:
        raise ValueError("max_related_items must be at least 1")
    if limits.max_record_bytes < 1:
        raise ValueError("max_record_bytes must be at least 1")
    if limits.cache_entries < 1:
        raise ValueError("cache_entries must be at least 1")
    if limits.cache_bytes < 1:
        raise ValueError("cache_bytes must be at least 1")
