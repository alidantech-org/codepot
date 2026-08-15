from __future__ import annotations

import pytest

from dryv.features.ir import BoundedRecordIndex, IRFeature, IRRuntimeError
from dryv.ir import Contract


def test_ir_runtime_builds_reverse_indexes_and_dependencies(connected_contract: Contract) -> None:
    snapshot = IRFeature().load_contract(connected_contract)
    assert snapshot.valid

    operation = connected_contract.groups[0].operations[0]
    listener = connected_contract.groups[0].operations[2]
    event = connected_contract.groups[0].events[0]
    schema = connected_contract.groups[0].schemas[0]
    mapping = connected_contract.groups[0].storage_mappings[0]

    assert operation.id in snapshot.derived.event_emitters[event.id]
    assert listener.id in snapshot.derived.event_listeners[event.id]
    assert operation.id in snapshot.derived.schema_operations[schema.id]
    assert mapping.id in snapshot.derived.schema_storage_mappings[schema.id]
    assert schema.id in snapshot.direct_dependencies(operation.id)
    assert operation.id in snapshot.direct_dependents(schema.id)


def test_ir_runtime_resolves_effective_schema(connected_contract: Contract) -> None:
    snapshot = IRFeature().load_contract(connected_contract)
    schema = connected_contract.groups[0].schemas[0]
    effective = snapshot.effective_schema(schema.id)
    assert effective.schema is schema
    assert tuple(item.id for item in effective.fields) == tuple(item.id for item in schema.fields)


def test_bounded_record_index_is_deterministic_and_rejects_duplicates() -> None:
    index = BoundedRecordIndex.from_records(("b", "a"), id_of=lambda value: value)
    assert index.ids() == ("a", "b")
    with pytest.raises(IRRuntimeError) as caught:
        BoundedRecordIndex.from_records(("a", "a"), id_of=lambda value: value)
    assert caught.value.code == "IR_RUNTIME_DUPLICATE_RECORD"
