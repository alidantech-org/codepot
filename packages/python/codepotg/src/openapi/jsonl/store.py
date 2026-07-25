from __future__ import annotations

import hashlib
import json
from collections import OrderedDict
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from threading import Lock, RLock
from typing import Any, BinaryIO

from core.system_resources import tune_runtime

from .errors import JsonlLookupError
from .hot_index import HotIndexRegistry
from .indexing import index_shard, section_file
from .models import HotIndexLimits, RecordLocation
from .sqlite_index import SqliteIndexReader, sqlite_index_path


@dataclass(slots=True)
class _OpenSection:
    stream: BinaryIO
    lock: Lock


class _SectionReaderPool:
    """Reuse open section handles and serialize seek/read per file."""

    def __init__(self, root: Path, *, max_open: int) -> None:
        self.root = root
        self.max_open = max(1, max_open)
        self._states: OrderedDict[str, _OpenSection] = OrderedDict()
        self._lock = RLock()
        self._closed = False

    def read(self, relative: str, offset: int, length: int) -> bytes:
        state = self._state(relative)
        try:
            with state.lock:
                state.stream.seek(offset)
                return state.stream.read(length)
        except OSError as exc:
            raise JsonlLookupError(
                f"Unable to read indexed JSONL record: {relative}@{offset}"
            ) from exc

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            for state in self._states.values():
                state.stream.close()
            self._states.clear()
            self._closed = True

    def _state(self, relative: str) -> _OpenSection:
        with self._lock:
            if self._closed:
                raise JsonlLookupError("JSONL section reader is closed")
            state = self._states.get(relative)
            if state is not None:
                self._states.move_to_end(relative)
                return state
            path = self.root / Path(*PurePosixPath(relative).parts)
            try:
                state = _OpenSection(stream=path.open("rb"), lock=Lock())
            except OSError as exc:
                raise JsonlLookupError(f"Unable to open JSONL section: {path}") from exc
            self._states[relative] = state
            if len(self._states) > self.max_open:
                _, oldest = self._states.popitem(last=False)
                oldest.stream.close()
            return state


class JsonlIndexStore:
    def __init__(
        self,
        cache_dir: str | Path,
        *,
        hot_index: HotIndexRegistry | None = None,
    ) -> None:
        self.cache_dir = Path(cache_dir)
        tuning = tune_runtime(_source_size(self.cache_dir))
        effective_limits = HotIndexLimits(
            max_entries=tuning.hot_index_entries,
            max_bytes=tuning.hot_index_bytes,
        )
        self.hot_index = hot_index if hot_index is not None else HotIndexRegistry(
            effective_limits
        )
        self._sqlite = (
            SqliteIndexReader(
                self.cache_dir,
                cache_bytes=tuning.sqlite_cache_bytes,
            )
            if sqlite_index_path(self.cache_dir).is_file()
            else None
        )
        self._sections = _SectionReaderPool(
            self.cache_dir,
            max_open=min(64, max(8, tuning.cpu_count * 2)),
        )
        self._closed = False

    def get_by_ref(self, ref: str) -> RecordLocation | None:
        return self._lookup_definition("ref", ref)

    def get_by_key(self, key: str) -> RecordLocation | None:
        return self._lookup_definition("key", key)

    def get_by_operation_id(self, operation_id: str) -> RecordLocation | None:
        return self._lookup_definition("operationId", operation_id)

    def iter_locations(
        self,
        section: str,
        *,
        kinds: Sequence[str] = (),
        mention: tuple[str, str] | None = None,
    ) -> Iterator[RecordLocation]:
        """Enumerate lightweight handles without parsing raw JSONL records."""
        if self._sqlite is not None:
            yield from self._sqlite.locations(
                section,
                kinds=kinds,
                mention=mention,
            )
            return

        relative = section_file(section)
        path = self._cache_file(relative)
        if not path.is_file():
            return
        with path.open("rb") as stream:
            while raw_line := stream.readline():
                offset = stream.tell() - len(raw_line)
                line = raw_line[:-1] if raw_line.endswith(b"\n") else raw_line
                try:
                    envelope = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise JsonlLookupError(f"Invalid section JSONL line in {path}") from exc
                if not isinstance(envelope, Mapping):
                    continue
                location = _location_from_envelope(section, relative, offset, line, envelope)
                if kinds and location.kind not in kinds:
                    continue
                if mention is not None:
                    facts = self.find_mentions(*mention)
                    if not any(fact.get("item") == location.key for fact in facts):
                        continue
                yield location

    def find_mentions(self, index: str, value: str) -> tuple[Mapping[str, Any], ...]:
        cached = self.hot_index.get_query(index, value)
        if isinstance(cached, tuple):
            return cached
        facts = (
            self._sqlite.mentions(index, value)
            if self._sqlite is not None
            else tuple(self._scan_index("mentions", index, value))
        )
        self.hot_index.put_query(index, value, facts)
        return facts

    def iter_mentions(self, index: str) -> Iterator[Mapping[str, Any]]:
        if self._sqlite is not None:
            yield from self._sqlite.iter_mentions(index)
            return
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
        facts = (
            self._sqlite.dependants(ref)
            if self._sqlite is not None
            else tuple(self._scan_index("dependencies", "ref", ref, match_field="to"))
        )
        self.hot_index.put_query(cache_index, ref, facts)
        return facts

    def read_location(self, location: RecordLocation, *, verify: bool = True) -> Any:
        line = self._sections.read(location.file, location.offset, location.length)
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

    def close(self) -> None:
        if self._closed:
            return
        self._sections.close()
        if self._sqlite is not None:
            self._sqlite.close()
        self._closed = True

    def _lookup_definition(self, lookup: str, value: str) -> RecordLocation | None:
        cached = self.hot_index.get_definition(lookup, value)
        if isinstance(cached, RecordLocation):
            return cached
        if self._sqlite is not None:
            location = self._sqlite.definition(lookup, value)
            if location is not None:
                self.hot_index.put_definition(lookup, value, location)
            return location
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


def _location_from_envelope(
    section: str,
    relative: str,
    offset: int,
    line: bytes,
    envelope: Mapping[str, Any],
) -> RecordLocation:
    key = envelope.get("key")
    if not isinstance(key, str) or not key:
        raise JsonlLookupError(f"Section record is missing a stable key: {relative}@{offset}")
    resources = envelope.get("resources", ())
    return RecordLocation(
        section=section,
        file=relative,
        offset=offset,
        length=len(line),
        sha256=f"sha256:{hashlib.sha256(line).hexdigest()}",
        key=key,
        ref=str(envelope["ref"]) if envelope.get("ref") is not None else None,
        kind=str(envelope["kind"]) if envelope.get("kind") is not None else None,
        resources=tuple(str(item) for item in resources),
    )


def _source_size(cache_dir: Path) -> int:
    try:
        with (cache_dir / "manifest.json").open("r", encoding="utf-8") as stream:
            manifest = json.load(stream)
        source = manifest.get("source", {})
        return int(source.get("size", source.get("originalSize", 0)))
    except (OSError, ValueError, TypeError, json.JSONDecodeError, AttributeError):
        return 0


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
