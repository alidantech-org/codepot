from __future__ import annotations

import pytest

from dryv.features.serialization import (
    RepresentationRecord,
    SerializationError,
    canonical_record_hash,
    contract_from_jsonl,
    contract_from_records,
    contract_to_jsonl,
    contract_to_records,
)
from dryv.ir import (
    Contract,
    Group,
    Name,
    Schema,
    SchemaField,
    SchemaKind,
    SemanticId,
    TypeExpression,
)


def _contract() -> Contract:
    identifier = SchemaField(
        id=SemanticId("user.field.id"),
        name=Name("id"),
        type=TypeExpression.primitive("string"),
        required=True,
    )
    user = Schema(
        id=SemanticId("user.schema"),
        name=Name("User"),
        kind=SchemaKind.OBJECT,
        fields=(identifier,),
    )
    group = Group(
        id=SemanticId("user.group"),
        name=Name("Users"),
        schemas=(user,),
    )
    return Contract(
        id=SemanticId("example.contract"),
        name=Name("Example"),
        groups=(group,),
    )


def test_contract_is_split_into_stable_semantic_records_and_reconstructed() -> None:
    contract = _contract()
    records = contract_to_records(contract)

    assert tuple(record.id for record in records) == tuple(
        sorted(record.id for record in records)
    )
    assert {record.kind for record in records} >= {
        "Contract",
        "Group",
        "Schema",
        "SchemaField",
    }
    assert contract_from_records(records) == contract


def test_contract_jsonl_round_trip_is_record_streamed() -> None:
    contract = _contract()
    payload = b"".join(contract_to_jsonl(contract))

    assert payload.count(b"\n") == len(contract_to_records(contract))
    assert payload.count(b"\n") > 1

    chunks = (payload[:11], payload[11:37], payload[37:])
    assert contract_from_jsonl(chunks) == contract


def test_canonical_record_hash_is_stable() -> None:
    record = contract_to_records(_contract())[0]
    first = canonical_record_hash(record)
    second = canonical_record_hash(record)

    assert first == second
    assert first.startswith("sha256:")
    assert len(first) == len("sha256:") + 64


def test_contract_record_reconstruction_rejects_missing_owned_record() -> None:
    records = contract_to_records(_contract())
    incomplete = tuple(record for record in records if record.kind != "Schema")

    with pytest.raises(SerializationError) as raised:
        contract_from_records(incomplete)

    assert raised.value.code == "SERIALIZATION_MISSING_RECORD"


def test_contract_record_reconstruction_rejects_duplicate_ids() -> None:
    records = contract_to_records(_contract())
    duplicate = RepresentationRecord(records[0].id, records[0].kind, records[0].value)

    with pytest.raises(SerializationError) as raised:
        contract_from_records((*records, duplicate))

    assert raised.value.code == "SERIALIZATION_DUPLICATE_RECORD_ID"
