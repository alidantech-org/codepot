from __future__ import annotations

import hashlib
import json
from collections import OrderedDict
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO

from .hot_index import HotIndexRegistry
from .models import ExtractedRecord, RecordLocation, SectionManifest

_HTTP_METHODS = frozenset(
    {"get", "put", "post", "delete", "patch", "options", "head", "trace"}
)
_COMPONENT_PREFIXES = {
    "schemas": "schema",
    "parameters": "parameter",
    "requestBodies": "request-body",
    "responses": "response",
    "securitySchemes": "security-scheme",
    "headers": "header",
    "examples": "example",
    "links": "link",
    "callbacks": "callback",
    "pathItems": "path-item",
}
_X_CODEGEN_PREFIXES = {
    "resources": "resource",
    "frontends": "frontend",
    "access": "access",
    "baseEntities": "base-entity",
    "entities": "entity",
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def json_pointer_escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def section_file(section: str) -> str:
    if section == "paths":
        return "paths.jsonl"
    return PurePosixPath(section).with_suffix(".jsonl").as_posix()


@dataclass(frozen=True, slots=True)
class ClassifiedRecord:
    key: str
    ref: str | None
    kind: str | None
    resources: tuple[str, ...]


@dataclass(slots=True)
class _SectionState:
    file: str
    stream: BinaryIO
    hasher: Any
    count: int = 0
    bytes: int = 0


class SectionWriter:
    def __init__(self, root: Path) -> None:
        self._root = root
        self._states: dict[str, _SectionState] = {}

    def write(
        self,
        record: ExtractedRecord,
        classification: ClassifiedRecord,
    ) -> RecordLocation:
        state = self._state(record.section)
        envelope = {
            "key": classification.key,
            "ref": classification.ref,
            "kind": classification.kind,
            "resources": list(classification.resources),
            "raw": record.raw,
        }
        line = canonical_json_bytes(envelope)
        digest = f"sha256:{hashlib.sha256(line).hexdigest()}"
        offset = state.stream.tell()
        state.stream.write(line)
        state.stream.write(b"\n")
        state.hasher.update(line)
        state.hasher.update(b"\n")
        state.count += 1
        state.bytes += len(line) + 1
        return RecordLocation(
            section=record.section,
            file=state.file,
            offset=offset,
            length=len(line),
            sha256=digest,
            key=classification.key,
            ref=classification.ref,
            kind=classification.kind,
            resources=classification.resources,
        )

    def close(self) -> dict[str, SectionManifest]:
        manifests: dict[str, SectionManifest] = {}
        for section, state in self._states.items():
            state.stream.flush()
            state.stream.close()
            manifests[section] = SectionManifest(
                file=state.file,
                count=state.count,
                bytes=state.bytes,
                sha256=f"sha256:{state.hasher.hexdigest()}",
            )
        self._states.clear()
        return manifests

    def _state(self, section: str) -> _SectionState:
        state = self._states.get(section)
        if state is not None:
            return state
        relative = section_file(section)
        path = self._root / Path(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        state = _SectionState(
            file=relative,
            stream=path.open("wb"),
            hasher=hashlib.sha256(),
        )
        self._states[section] = state
        return state


class _OpenWriterPool:
    def __init__(self, root: Path, *, max_open: int = 32) -> None:
        self._root = root
        self._max_open = max_open
        self._streams: OrderedDict[str, BinaryIO] = OrderedDict()

    def append(self, relative: str, data: bytes) -> None:
        stream = self._streams.get(relative)
        if stream is None:
            path = self._root / Path(relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            stream = path.open("ab")
            self._streams[relative] = stream
        self._streams.move_to_end(relative)
        stream.write(data)
        if len(self._streams) > self._max_open:
            _, oldest = self._streams.popitem(last=False)
            oldest.flush()
            oldest.close()

    def close(self) -> None:
        for stream in self._streams.values():
            stream.flush()
            stream.close()
        self._streams.clear()


class ShardedIndexWriter:
    def __init__(self, root: Path, *, shard_chars: int = 1, max_open: int = 32) -> None:
        self._root = root
        self._shard_chars = shard_chars
        self._pool = _OpenWriterPool(root, max_open=max_open)
        self.counts: dict[str, int] = {
            "definitions": 0,
            "mentions": 0,
            "dependencies": 0,
        }
        self.shards: dict[str, set[str]] = {
            "definitions": set(),
            "mentions": set(),
            "dependencies": set(),
        }

    def definition(
        self,
        lookup: str,
        value: str,
        location: RecordLocation,
        *,
        hot_index: HotIndexRegistry,
    ) -> None:
        fact = {"lookup": lookup, "value": value, "record": location.to_json()}
        self._write("definitions", lookup, value, fact)
        hot_index.put_definition(lookup, value, location)

    def mention(
        self,
        index: str,
        value: str,
        *,
        item: str,
        purpose: str,
        file: str,
    ) -> None:
        fact = {
            "index": index,
            "value": value,
            "item": item,
            "purpose": purpose,
            "file": file,
        }
        self._write("mentions", index, value, fact)

    def dependency(
        self,
        *,
        source: str,
        target: str,
        purpose: str,
        file: str,
    ) -> None:
        fact = {"from": source, "to": target, "purpose": purpose, "file": file}
        self._write("dependencies", "ref", target, fact)

    def close(self) -> None:
        self._pool.close()

    def manifest(self) -> dict[str, Any]:
        return {
            category: {
                "directory": f"indexes/{category}",
                "records": self.counts[category],
                "shards": sorted(self.shards[category]),
                "shardChars": self._shard_chars,
            }
            for category in ("definitions", "mentions", "dependencies")
        }

    def _write(
        self,
        category: str,
        index: str,
        value: str,
        fact: Mapping[str, Any],
    ) -> None:
        shard = index_shard(index, value, chars=self._shard_chars)
        relative = f"indexes/{category}/{shard}.jsonl"
        self._pool.append(relative, canonical_json_bytes(fact) + b"\n")
        self.counts[category] += 1
        self.shards[category].add(shard)


def index_shard(index: str, value: str, *, chars: int = 1) -> str:
    digest = hashlib.sha256(f"{index}\0{value}".encode()).hexdigest()
    return digest[:chars]


def classify_record(record: ExtractedRecord) -> ClassifiedRecord:
    section = record.section
    name = record.name
    raw = record.raw
    resources = set(extract_resource_mentions(raw))

    if section == "paths":
        return ClassifiedRecord(
            key=f"path:{name}",
            ref=f"#/paths/{json_pointer_escape(name)}",
            kind="path",
            resources=tuple(sorted(resources)),
        )

    group, collection = section.split("/", 1)
    escaped = json_pointer_escape(name)
    if group == "components":
        prefix = _COMPONENT_PREFIXES.get(collection, collection.rstrip("s"))
        kind = _schema_kind(raw) if collection == "schemas" else prefix
        return ClassifiedRecord(
            key=f"{prefix}:{name}",
            ref=f"#/components/{collection}/{escaped}",
            kind=kind,
            resources=tuple(sorted(resources)),
        )

    prefix = _X_CODEGEN_PREFIXES.get(collection, collection.rstrip("s"))
    if collection == "resources":
        resources.add(name)
    return ClassifiedRecord(
        key=f"{prefix}:{name}",
        ref=f"#/x-codegen/{collection}/{escaped}",
        kind=prefix,
        resources=tuple(sorted(resources)),
    )


def register_record_indexes(
    record: ExtractedRecord,
    classification: ClassifiedRecord,
    location: RecordLocation,
    *,
    indexes: ShardedIndexWriter,
    hot_index: HotIndexRegistry,
) -> tuple[int, int, int]:
    definitions = 0
    mentions = 0
    dependencies = 0

    indexes.definition("key", classification.key, location, hot_index=hot_index)
    definitions += 1
    if classification.ref is not None:
        indexes.definition("ref", classification.ref, location, hot_index=hot_index)
        definitions += 1

    for resource in classification.resources:
        indexes.mention(
            "resource",
            resource,
            item=classification.key,
            purpose="record.resource",
            file=location.file,
        )
        mentions += 1

    for ref, purpose in extract_ref_mentions(record.raw):
        indexes.mention(
            "ref",
            ref,
            item=classification.key,
            purpose=purpose,
            file=location.file,
        )
        indexes.dependency(
            source=classification.key,
            target=ref,
            purpose=purpose,
            file=location.file,
        )
        mentions += 1
        dependencies += 1

    for resource, purpose in extract_explicit_resource_mentions(record.raw):
        indexes.mention(
            "resource",
            resource,
            item=classification.key,
            purpose=purpose,
            file=location.file,
        )
        mentions += 1

    for tag, purpose in extract_tag_mentions(record.raw):
        indexes.mention(
            "tag",
            tag,
            item=classification.key,
            purpose=purpose,
            file=location.file,
        )
        mentions += 1

    if record.section == "paths" and isinstance(record.raw, Mapping):
        for method, operation in record.raw.items():
            lowered = str(method).lower()
            if lowered not in _HTTP_METHODS or not isinstance(operation, Mapping):
                continue
            operation_key = f"operation:{lowered}:{record.name}"
            operation_ref = f"{classification.ref}/{lowered}"
            operation_location = RecordLocation(
                section=location.section,
                file=location.file,
                offset=location.offset,
                length=location.length,
                sha256=location.sha256,
                key=operation_key,
                ref=operation_ref,
                kind="operation",
                resources=location.resources,
                pointer=f"/{json_pointer_escape(lowered)}",
            )
            indexes.definition(
                "key",
                operation_key,
                operation_location,
                hot_index=hot_index,
            )
            indexes.definition(
                "ref",
                operation_ref,
                operation_location,
                hot_index=hot_index,
            )
            definitions += 2
            operation_id = operation.get("operationId")
            if isinstance(operation_id, str) and operation_id:
                indexes.definition(
                    "operationId",
                    operation_id,
                    operation_location,
                    hot_index=hot_index,
                )
                definitions += 1

    return definitions, mentions, dependencies


def extract_ref_mentions(value: Any) -> Iterator[tuple[str, str]]:
    yield from _walk_ref_mentions(value, path=())


def _walk_ref_mentions(
    value: Any,
    *,
    path: tuple[str, ...],
) -> Iterator[tuple[str, str]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = (*path, str(key))
            if key == "$ref" and isinstance(child, str):
                yield child, ".".join(path) or "$ref"
            else:
                yield from _walk_ref_mentions(child, path=child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_ref_mentions(child, path=(*path, str(index)))


def extract_resource_mentions(value: Any) -> Iterable[str]:
    seen: set[str] = set()
    for resource, _ in extract_explicit_resource_mentions(value):
        seen.add(resource)
    return seen


def extract_explicit_resource_mentions(value: Any) -> Iterator[tuple[str, str]]:
    yield from _walk_resource_mentions(value, path=())


def _walk_resource_mentions(
    value: Any,
    *,
    path: tuple[str, ...],
) -> Iterator[tuple[str, str]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = (*path, str(key))
            purpose = ".".join(child_path)
            if key == "resource":
                if isinstance(child, str) and child:
                    yield child, purpose
                elif isinstance(child, Mapping):
                    name = child.get("name")
                    if isinstance(name, str) and name:
                        yield name, purpose
            if key == "$ref" and isinstance(child, str):
                prefix = "#/x-codegen/resources/"
                if child.startswith(prefix):
                    resource = child[len(prefix) :].split("/", 1)[0]
                    if resource:
                        yield resource.replace("~1", "/").replace("~0", "~"), purpose
            yield from _walk_resource_mentions(child, path=child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_resource_mentions(child, path=(*path, str(index)))


def extract_tag_mentions(value: Any) -> Iterator[tuple[str, str]]:
    yield from _walk_tag_mentions(value, path=())


def _walk_tag_mentions(
    value: Any,
    *,
    path: tuple[str, ...],
) -> Iterator[tuple[str, str]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = (*path, str(key))
            if key == "tags" and isinstance(child, list):
                for item in child:
                    if isinstance(item, str) and item:
                        yield item, ".".join(child_path)
            yield from _walk_tag_mentions(child, path=child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_tag_mentions(child, path=(*path, str(index)))


def _schema_kind(raw: Any) -> str:
    if isinstance(raw, Mapping):
        codegen = raw.get("x-codegen")
        if isinstance(codegen, Mapping):
            kind = codegen.get("kind")
            if isinstance(kind, str) and kind:
                return kind
        enum = raw.get("enum")
        if isinstance(enum, list):
            return "enum"
        schema_type = raw.get("type")
        if isinstance(schema_type, str) and schema_type:
            return schema_type
    return "schema"
