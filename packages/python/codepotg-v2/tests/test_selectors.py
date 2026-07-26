from __future__ import annotations

import pytest

from codepotg.ir import Contract
from codepotg.selectors import DEFAULT_SELECTOR_REGISTRY


def test_fixed_selectors_return_typed_group_rooted_contexts(
    connected_contract: Contract,
) -> None:
    operations = DEFAULT_SELECTOR_REGISTRY.select(
        "groups.operations.each",
        connected_contract,
    )
    storage = DEFAULT_SELECTOR_REGISTRY.select(
        "groups.storage.mappings.each",
        connected_contract,
    )
    workflows = DEFAULT_SELECTOR_REGISTRY.select(
        "groups.workflows.each",
        connected_contract,
    )

    assert len(operations) == 3
    assert all(context.group is connected_contract.groups[0] for context in operations)
    assert [context.operation.name.camel.original for context in operations if context.operation] == [
        "createUser",
        "deleteUser",
        "auditUserCreated",
    ]
    assert storage[0].storage_mapping is connected_contract.groups[0].storage_mappings[0]
    assert workflows[0].workflow is connected_contract.groups[0].workflows[0]


def test_selector_registry_is_closed_and_introspectable(connected_contract: Contract) -> None:
    ids = tuple(item.id for item in DEFAULT_SELECTOR_REGISTRY.descriptors)

    assert ids == tuple(sorted(ids))
    assert "groups.operations.each" in ids
    assert "resources.each" not in ids
    assert "schemas.models.each" not in ids
    assert "http.groups.each" not in ids

    with pytest.raises(KeyError, match="unknown fixed selector"):
        DEFAULT_SELECTOR_REGISTRY.select("groups.billing.each", connected_contract)
