from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator, Mapping
from pathlib import Path, PurePosixPath
from typing import Any

from .errors import JsonlLookupError
from .hot_index import HotIndexRegistry
from .indexing import index_shard
from .models import RecordLocation


class JsonlIndexStore:
    def __init__(
        self,
        cache_dir: str | Path,
        *,
        hot_index: HotIndexRegistry | None = None,
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.hot_index = hot_index or HotIndexRegistry()

    def get_by_ref(self, ref: str) -> RecordLocation | None:
        return self._lookup_definition("ref", ref)

    def get_by_key(self, key: str) -> RecordLocation | None:
        return self._lookup_definition("key", key)

    def get_by_operation_id(self, operation_id: str) -> RecordLocation | None:
        return self._lookup_definition("operationId", operation_id)

    def find_mentions(self, index: str, value: str) -> tuple[Mapping[str, Any], ...]:
        cached = self.hot_index.get_query(index, value)
        if isinstance(cached, tuple):
            return cached
        facts = tuple(self._scan_index("mentions", index, value))
        self.hot_index.put_query(index, value, facts)
        return facts

    def iter_mentions(self, index: str) -> Iterator[Mapping[str, Any]]:
        """Stream every fact for one mention index across deterministic shards."""

        directory = self._cache_file("indexes/mentions")
        if not directory.is_dir():
            return
        for path in sorted(directory.glob("*.jsonl")):
            try:
                with path.open("rb") as stream:
                    for raw_line in stream:
                        try:
                            fact = json.loads(raw_line)
                        except json.JSONDecodeError as exc:
                            raise JsonlLookupError(
                                f"Invalid index JSONL line in {path}"
                            ) from exc
                        if (
                            isinstance(fact, Mapping)
                            and fact.get("index") == index
                            and isinstance(fact.get("value"), str)
                        ):
                            yield fact
            except OSError as exc:
                raise JsonlLookupError(f"Unable to stream JSONL index: {path}") from exc

    def find_dependants(self, ref: str) -> tuple[Mapping[str, Any], ...]:
        cache_index = "dependency"
        cached = self.hot_index.get_query(cache_index, ref)
        if isinstance(cached, tuple):
            return cached
        facts = tuple(self._scan_index("dependencies", "ref", ref, match_field="to"))
        self.hot_index.put_query(cache_index, ref, facts)
        return facts

    def read_location(self, location: RecordLocation, *, verify: bool = True) -> Any:
        path = self._cache_file(location.file)
        try:
            with path.open("rb") as stream:
                stream.seek(location.offset)
                line = stream.read(location.length)
        except OSError as exc:
            raise JsonlLookupError(f"Unable to read indexed JSONL record: {path}") from exc
        if len(line) != location.length:
            raise JsonlLookupError(
                f"Indexed JSONL record is truncated: {location.file}@{location.offset}"
            )
        if verify:
            digest = f"sha256:{hashlib.sha256(line).hexdigest()}"
            if digest != location.sha256:
                raise JsonlLookupError(
                    f"Indexed JSONL record hash mismatch: {location.file}@{location.offset}"
                )
        try:
            envelope = json.loads(line)
        except json.JSONDecodeError as exc:
            raise JsonlLookupError(
                f"Indexed JSONL record is invalid JSON: {location.file}@{location.offset}"
            ) from exc
        value = envelope.get("raw")
        if location.pointer:
            value = _resolve_pointer(value, location.pointer)
        return value

    def resolve_ref(self, ref: str, *, verify: bool = True) -> Any | None:
        location = self.get_by_ref(ref)
        if location is None:
            return None
        return self.read_location(location, verify=verify)

    def _lookup_definition(self, lookup: str, value: str) -> RecordLocation | None:
        cached = self.hot_index.get_definition(lookup, value)
        if isinstance(cached, RecordLocation):
            return cached
        for fact in self._scan_index("definitions", lookup, value):
            record = fact.get("record")
            if not isinstance(record, Mapping):
                continue
            location = RecordLocation.from_json(record)
            self.hot_index.put_definition(lookup, value, location)
            return location
        return None

    def _scan_index(
        self,
        category: str,
        index: str,
        value: str,
        *,
        match_field: str = "value",
    ) -> Iterator[Mapping[str, Any]]:
        shard = index_shard(index, value)
        path = self._cache_file(f"indexes/{category}/{shard}.jsonl")
        if not path.exists():
            return
        with path.open("rb") as stream:
            for raw_line in stream:
                try:
                    fact = json.loads(raw_line)
                except json.JSONDecodeError as exc:
                    raise JsonlLookupError(f"Invalid index JSONL line in {path}") from exc
                if category == "definitions":
                    matches = fact.get("lookup") == index and fact.get("value") == value
                elif category == "dependencies":
                    matches = fact.get(match_field) == value
                else:
                    matches = fact.get("index") == index and fact.get("value") == value
                if matches:
                    yield fact

    def _cache_file(self, relative: str) -> Path:
        if "\\" in relative:
            raise JsonlLookupError(f"Indexed cache path is not normalized: {relative}")
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts:
            raise JsonlLookupError(f"Indexed cache path is unsafe: {relative}")
        return self.cache_dir / Path(*pure.parts)


def _resolve_pointer(value: Any, pointer: str) -> Any:
    if pointer == "":
        return value
    if not pointer.startswith("/"):
        raise JsonlLookupError(f"Invalid JSON pointer in index: {pointer}")
    current = value
    for token in pointer[1:].split("/"):
        decoded = token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, Mapping):
            if decoded not in current:
                raise JsonlLookupError(f"JSON pointer does not exist: {pointer}")
            current = current[decoded]
        elif isinstance(current, list):
            try:
                current = current[int(decoded)]
            except (ValueError, IndexError) as exc:
                raise JsonlLookupError(f"JSON pointer does not exist: {pointer}") from exc
        else:
            raise JsonlLookupError(f"JSON pointer traverses a scalar: {pointer}")
    return current
