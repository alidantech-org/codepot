from __future__ import annotations

from hashlib import sha256
from typing import BinaryIO, Iterable, Iterator

from dryv.ir import Contract
from dryv.versions import IR_API_VERSION

from .ir_codec import contract_from_document, contract_to_document
from .records import (
    PortableValue,
    RepresentationRecord,
    SerializationError,
    canonical_json_bytes,
    encode_jsonl,
    iter_jsonl,
)

_RECORD_REF_KIND = "record-ref"
_RECORD_REF_MARKER = "$dryv"
_RECORD_REF_ID = "id"


def contract_to_records(contract: Contract) -> tuple[RepresentationRecord, ...]:
    """Split one canonical Contract document into stable semantic records.

    Dataclass records that carry a canonical semantic ``id`` become independent
    records. Their containment positions are replaced with explicit
    serialization-only record references. Ordinary ``SemanticId`` references
    remain unchanged, so authored relationships are not rewritten as ownership.
    """

    document = contract_to_document(contract)
    encoded = document.get("contract")
    records: dict[str, RepresentationRecord] = {}

    root = _extract_records(encoded, records)
    if not _is_record_ref(root):
        raise SerializationError(
            "SERIALIZATION_CONTRACT_RECORD",
            "canonical Contract did not produce a semantic root record",
        )

    return tuple(records[key] for key in sorted(records))


def contract_from_records(records: Iterable[RepresentationRecord]) -> Contract:
    """Reconstruct one canonical Contract from semantic representation records."""

    by_id: dict[str, RepresentationRecord] = {}
    roots: list[str] = []
    for record in records:
        if record.id in by_id:
            raise SerializationError(
                "SERIALIZATION_DUPLICATE_RECORD_ID",
                f"duplicate semantic record id {record.id!r}",
            )
        by_id[record.id] = record
        if record.kind == "Contract":
            roots.append(record.id)

    if len(roots) != 1:
        raise SerializationError(
            "SERIALIZATION_CONTRACT_ROOT",
            "semantic record stream must contain exactly one Contract record",
        )

    expanded = _expand_record(roots[0], by_id, active=set())
    document = {
        "contract": expanded,
        "format": "codepot-ir",
        "irVersion": str(IR_API_VERSION),
    }
    return contract_from_document(document)


def contract_to_jsonl(contract: Contract) -> Iterator[bytes]:
    """Encode a Contract as bounded, record-addressable canonical JSONL."""

    return encode_jsonl(contract_to_records(contract))


def contract_from_jsonl(
    chunks: Iterable[bytes] | BinaryIO,
    *,
    max_record_bytes: int = 1024 * 1024,
) -> Contract:
    """Decode a canonical JSONL record stream into a Contract.

    ``iter_jsonl`` remains the scalable record-by-record API. Reconstructing a
    Python Contract necessarily materializes the semantic records required by
    that Contract.
    """

    return contract_from_records(
        iter_jsonl(chunks, max_record_bytes=max_record_bytes)
    )


def canonical_record_bytes(record: RepresentationRecord) -> bytes:
    """Canonical bytes used by protocol boundaries and per-record hashing."""

    value: PortableValue = {
        "id": record.id,
        "kind": record.kind,
        "value": record.value,
    }
    return canonical_json_bytes(value)


def canonical_record_hash(record: RepresentationRecord) -> str:
    return f"sha256:{sha256(canonical_record_bytes(record)).hexdigest()}"


def _extract_records(
    value: object,
    records: dict[str, RepresentationRecord],
) -> PortableValue:
    if isinstance(value, dict):
        record_id = _semantic_record_id(value)
        if record_id is not None:
            kind = value.get("$type")
            assert isinstance(kind, str)
            payload = {
                key: _extract_records(item, records)
                for key, item in sorted(value.items())
            }
            record = RepresentationRecord(record_id, kind, payload)
            if record_id in records:
                raise SerializationError(
                    "SERIALIZATION_DUPLICATE_RECORD_ID",
                    f"canonical Contract contains duplicate semantic id {record_id!r}",
                )
            records[record_id] = record
            return _record_ref(record_id)
        return {
            str(key): _extract_records(item, records)
            for key, item in sorted(value.items())
        }
    if isinstance(value, list):
        return [_extract_records(item, records) for item in value]
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    raise SerializationError(
        "SERIALIZATION_CONTRACT_VALUE",
        f"unsupported canonical Contract value {type(value).__name__}",
    )


def _semantic_record_id(value: dict[object, object]) -> str | None:
    type_name = value.get("$type")
    identity = value.get("id")
    if not isinstance(type_name, str) or not isinstance(identity, dict):
        return None
    if set(identity) != {"$ref"} or not isinstance(identity.get("$ref"), str):
        return None
    return identity["$ref"]


def _record_ref(record_id: str) -> dict[str, PortableValue]:
    return {
        _RECORD_REF_MARKER: _RECORD_REF_KIND,
        _RECORD_REF_ID: record_id,
    }


def _is_record_ref(value: object) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {_RECORD_REF_MARKER, _RECORD_REF_ID}
        and value.get(_RECORD_REF_MARKER) == _RECORD_REF_KIND
        and isinstance(value.get(_RECORD_REF_ID), str)
    )


def _expand_record(
    record_id: str,
    records: dict[str, RepresentationRecord],
    *,
    active: set[str],
) -> PortableValue:
    record = records.get(record_id)
    if record is None:
        raise SerializationError(
            "SERIALIZATION_MISSING_RECORD",
            f"semantic record reference {record_id!r} is missing",
        )
    if record_id in active:
        raise SerializationError(
            "SERIALIZATION_RECORD_CYCLE",
            f"semantic containment cycle includes {record_id!r}",
        )
    if not isinstance(record.value, dict):
        raise SerializationError(
            "SERIALIZATION_RECORD_VALUE",
            f"semantic record {record_id!r} must contain an object",
        )
    if record.value.get("$type") != record.kind:
        raise SerializationError(
            "SERIALIZATION_RECORD_KIND",
            f"semantic record {record_id!r} kind does not match its canonical type",
        )

    active.add(record_id)
    try:
        return _expand_value(record.value, records, active=active)
    finally:
        active.remove(record_id)


def _expand_value(
    value: PortableValue,
    records: dict[str, RepresentationRecord],
    *,
    active: set[str],
) -> PortableValue:
    if _is_record_ref(value):
        assert isinstance(value, dict)
        target = value[_RECORD_REF_ID]
        assert isinstance(target, str)
        return _expand_record(target, records, active=active)
    if isinstance(value, list):
        return [_expand_value(item, records, active=active) for item in value]
    if isinstance(value, dict):
        return {
            key: _expand_value(item, records, active=active)
            for key, item in sorted(value.items())
        }
    return value


__all__ = [
    "canonical_record_bytes",
    "canonical_record_hash",
    "contract_from_jsonl",
    "contract_from_records",
    "contract_to_jsonl",
    "contract_to_records",
]
