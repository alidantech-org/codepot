from __future__ import annotations

from dryv.features.serialization import (
    RepresentationRecord,
    SerializationError,
    canonical_json_bytes,
    decode_json,
    decode_yaml,
    encode_json,
    encode_jsonl,
    encode_yaml,
    iter_jsonl,
    iter_jsonl_indexed,
)


def _records() -> tuple[RepresentationRecord, ...]:
    return (
        RepresentationRecord("schema.user", "schema", {"name": "User", "fields": ["id", "email"]}),
        RepresentationRecord("operation.create", "operation", {"output": "schema.user"}),
    )


def test_json_and_yaml_normalize_to_same_records() -> None:
    records = _records()
    assert decode_json(encode_json(records)) == records
    assert decode_yaml(encode_yaml(records)) == records
    assert canonical_json_bytes(records[0].value) == canonical_json_bytes(decode_yaml(encode_yaml(records))[0].value)


def test_jsonl_streams_across_chunk_boundaries_with_stable_locations() -> None:
    records = _records()
    payload = b"".join(encode_jsonl(records))
    chunks = (payload[:7], payload[7:19], payload[19:])
    decoded = tuple(iter_jsonl(chunks))
    assert decoded == records

    indexed = tuple(iter_jsonl_indexed((payload,)))
    assert tuple(item[0] for item in indexed) == records
    assert indexed[0][1].offset == 0
    assert indexed[0][1].length + indexed[1][1].length == len(payload)


def test_jsonl_record_limit_is_bounded() -> None:
    payload = b"".join(encode_jsonl(_records()[:1]))
    try:
        tuple(iter_jsonl((payload,), max_record_bytes=8))
    except SerializationError as exc:
        assert exc.code == "SERIALIZATION_RECORD_LIMIT"
    else:
        raise AssertionError("oversized JSONL record must fail")


def test_jsonl_rejects_unsupported_version() -> None:
    payload = b"".join(encode_jsonl(_records()[:1]))
    mutated = payload.replace(b'"version":"2.0"', b'"version":"999"')
    if mutated == payload:
        mutated = payload.replace(b'"version":"', b'"version":"999-')
    try:
        tuple(iter_jsonl((mutated,)))
    except SerializationError as exc:
        assert exc.code == "SERIALIZATION_VERSION"
    else:
        raise AssertionError("unsupported JSONL version must fail")
