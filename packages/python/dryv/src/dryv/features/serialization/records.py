from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import BinaryIO, Iterable, Iterator, TypeAlias

import yaml

from dryv.versions import IR_API_VERSION

PortableScalar: TypeAlias = str | int | float | bool | None
PortableValue: TypeAlias = PortableScalar | list["PortableValue"] | dict[str, "PortableValue"]
_RECORD_FORMAT = "dryv-ir-record"
_DOCUMENT_FORMAT = "dryv-ir-records"
_DEFAULT_MAX_RECORD_BYTES = 1024 * 1024


class SerializationError(ValueError):
    def __init__(self, code: str, message: str, *, offset: int | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.offset = offset


@dataclass(frozen=True, slots=True)
class RepresentationRecord:
    id: str
    kind: str
    value: PortableValue

    def __post_init__(self) -> None:
        if not self.id.strip() or self.id.strip() != self.id:
            raise ValueError("representation record id must be a non-empty trimmed string")
        if not self.kind.strip() or self.kind.strip() != self.kind:
            raise ValueError("representation record kind must be a non-empty trimmed string")
        object.__setattr__(self, "value", canonicalize(self.value))


@dataclass(frozen=True, slots=True)
class RecordLocation:
    id: str
    offset: int
    length: int


def canonicalize(value: PortableValue) -> PortableValue:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise SerializationError("SERIALIZATION_NUMBER", "non-finite numbers are not portable")
        return value
    if isinstance(value, list):
        return [canonicalize(item) for item in value]
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise SerializationError("SERIALIZATION_KEY", "portable object keys must be strings")
        return {key: canonicalize(value[key]) for key in sorted(value)}
    raise SerializationError("SERIALIZATION_VALUE", f"unsupported portable value {type(value).__name__}")


def canonical_json_bytes(value: PortableValue) -> bytes:
    return json.dumps(canonicalize(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def encode_json(records: Iterable[RepresentationRecord]) -> bytes:
    envelope: PortableValue = {"format": _DOCUMENT_FORMAT, "version": str(IR_API_VERSION), "records": [_record_document(item) for item in records]}
    return canonical_json_bytes(envelope)


def decode_json(data: str | bytes) -> tuple[RepresentationRecord, ...]:
    try:
        text = data.decode("utf-8") if isinstance(data, bytes) else data
        value = json.loads(text, object_pairs_hook=_json_pairs)
    except UnicodeDecodeError as exc:
        raise SerializationError("SERIALIZATION_UTF8", "JSON must be UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise SerializationError("SERIALIZATION_JSON", f"invalid JSON at line {exc.lineno}, column {exc.colno}") from exc
    return _decode_envelope(value)


def encode_yaml(records: Iterable[RepresentationRecord]) -> bytes:
    document = {"format": _DOCUMENT_FORMAT, "version": str(IR_API_VERSION), "records": [_record_document(item) for item in records]}
    return yaml.safe_dump(document, allow_unicode=True, default_flow_style=False, sort_keys=True).encode("utf-8")


def decode_yaml(data: str | bytes) -> tuple[RepresentationRecord, ...]:
    try:
        text = data.decode("utf-8") if isinstance(data, bytes) else data
        value = yaml.safe_load(text)
    except UnicodeDecodeError as exc:
        raise SerializationError("SERIALIZATION_UTF8", "YAML must be UTF-8") from exc
    except yaml.YAMLError as exc:
        raise SerializationError("SERIALIZATION_YAML", "invalid YAML") from exc
    return _decode_envelope(value)


def encode_jsonl(records: Iterable[RepresentationRecord]) -> Iterator[bytes]:
    for record in records:
        yield canonical_json_bytes(_jsonl_document(record)) + b"\n"


def iter_jsonl(chunks: Iterable[bytes] | BinaryIO, *, max_record_bytes: int = _DEFAULT_MAX_RECORD_BYTES) -> Iterator[RepresentationRecord]:
    for record, _ in iter_jsonl_indexed(chunks, max_record_bytes=max_record_bytes):
        yield record


def iter_jsonl_indexed(chunks: Iterable[bytes] | BinaryIO, *, max_record_bytes: int = _DEFAULT_MAX_RECORD_BYTES) -> Iterator[tuple[RepresentationRecord, RecordLocation]]:
    if max_record_bytes < 1:
        raise ValueError("max_record_bytes must be positive")
    iterable: Iterable[bytes] = _file_chunks(chunks) if hasattr(chunks, "read") else chunks  # type: ignore[arg-type]
    buffer = bytearray()
    absolute = 0
    record_start = 0
    for chunk in iterable:
        if not isinstance(chunk, bytes):
            raise SerializationError("SERIALIZATION_CHUNK", "JSONL chunks must be bytes")
        buffer.extend(chunk)
        while True:
            newline = buffer.find(b"\n")
            if newline < 0:
                break
            line = bytes(buffer[:newline])
            del buffer[: newline + 1]
            length = newline + 1
            if len(line) > max_record_bytes:
                raise SerializationError("SERIALIZATION_RECORD_LIMIT", "JSONL record exceeds configured byte limit", offset=record_start)
            if line.strip():
                record = _decode_jsonl_line(line, record_start)
                yield record, RecordLocation(record.id, record_start, length)
            record_start += length
            absolute = record_start
        if len(buffer) > max_record_bytes:
            raise SerializationError("SERIALIZATION_RECORD_LIMIT", "JSONL record exceeds configured byte limit", offset=record_start)
    if buffer:
        if len(buffer) > max_record_bytes:
            raise SerializationError("SERIALIZATION_RECORD_LIMIT", "JSONL record exceeds configured byte limit", offset=record_start)
        record = _decode_jsonl_line(bytes(buffer), record_start)
        yield record, RecordLocation(record.id, record_start, len(buffer))
    del absolute


def decode_resource_bytes(data: bytes, media_type: str) -> tuple[RepresentationRecord, ...] | Iterator[RepresentationRecord]:
    normalized = media_type.split(";", 1)[0].strip().lower()
    if normalized in {"application/json", "application/vnd.dryv.ir+json"}:
        return decode_json(data)
    if normalized in {"application/yaml", "application/x-yaml", "text/yaml", "application/vnd.dryv.ir+yaml"}:
        return decode_yaml(data)
    if normalized in {"application/jsonl", "application/x-ndjson", "application/vnd.dryv.ir+jsonl"}:
        return iter_jsonl((data,))
    raise SerializationError("SERIALIZATION_MEDIA_TYPE", f"unsupported media type {media_type!r}")


def _record_document(record: RepresentationRecord) -> dict[str, PortableValue]:
    return {"id": record.id, "kind": record.kind, "value": record.value}


def _jsonl_document(record: RepresentationRecord) -> dict[str, PortableValue]:
    return {"format": _RECORD_FORMAT, "version": str(IR_API_VERSION), **_record_document(record)}


def _decode_envelope(value: object) -> tuple[RepresentationRecord, ...]:
    if not isinstance(value, dict):
        raise SerializationError("SERIALIZATION_ROOT", "representation document must be an object")
    if value.get("format") != _DOCUMENT_FORMAT:
        raise SerializationError("SERIALIZATION_FORMAT", "unsupported representation document format")
    if value.get("version") != str(IR_API_VERSION):
        raise SerializationError("SERIALIZATION_VERSION", f"representation requires IR version {IR_API_VERSION}")
    records = value.get("records")
    if not isinstance(records, list):
        raise SerializationError("SERIALIZATION_RECORDS", "representation document records must be an array")
    return tuple(_decode_record(item) for item in records)


def _decode_jsonl_line(line: bytes, offset: int) -> RepresentationRecord:
    try:
        value = json.loads(line.decode("utf-8"), object_pairs_hook=_json_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SerializationError("SERIALIZATION_JSONL", "invalid JSONL record", offset=offset) from exc
    if not isinstance(value, dict) or value.get("format") != _RECORD_FORMAT:
        raise SerializationError("SERIALIZATION_FORMAT", "unsupported JSONL record format", offset=offset)
    if value.get("version") != str(IR_API_VERSION):
        raise SerializationError("SERIALIZATION_VERSION", f"JSONL record requires IR version {IR_API_VERSION}", offset=offset)
    return _decode_record(value)


def _decode_record(value: object) -> RepresentationRecord:
    if not isinstance(value, dict):
        raise SerializationError("SERIALIZATION_RECORD", "record must be an object")
    unknown = set(value) - {"format", "version", "id", "kind", "value"}
    if unknown:
        raise SerializationError("SERIALIZATION_UNKNOWN_FIELD", f"unknown record field {sorted(unknown)[0]!r}")
    record_id = value.get("id")
    kind = value.get("kind")
    portable = value.get("value")
    if not isinstance(record_id, str) or not isinstance(kind, str):
        raise SerializationError("SERIALIZATION_RECORD", "record id and kind must be strings")
    return RepresentationRecord(record_id, kind, canonicalize(portable))  # type: ignore[arg-type]


def _json_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise SerializationError("SERIALIZATION_DUPLICATE_KEY", f"duplicate key {key!r}")
        result[key] = value
    return result


def _file_chunks(stream: BinaryIO, size: int = 64 * 1024) -> Iterator[bytes]:
    while True:
        chunk = stream.read(size)
        if not chunk:
            return
        yield chunk
