from __future__ import annotations

import pytest

from codepotg.generation import DEFAULT_SELECTOR_REGISTRY
from codepotg.ir import Contract


def test_fixed_selectors_use_published_roots_and_are_deterministic(
    connected_contract: Contract,
) -> None:
    selector_ids = tuple(item.id for item in DEFAULT_SELECTOR_REGISTRY.descriptors)

    assert selector_ids == tuple(sorted(selector_ids))
    assert {selector.split(".", 1)[0] for selector in selector_ids} == {
        "groups",
        "presentations",
    }
    operations = DEFAULT_SELECTOR_REGISTRY.select(
        "groups.operations.each",
        connected_contract,
    )
    assert [context.operation.name.camel.original for context in operations] == [
        "createUser",
        "deleteUser",
        "auditUserCreated",
    ]
    assert all(context.group is connected_contract.groups[0] for context in operations)


def test_arbitrary_selector_queries_are_rejected(connected_contract: Contract) -> None:
    with pytest.raises(KeyError, match="unknown fixed selector"):
        DEFAULT_SELECTOR_REGISTRY.select(
            "operations.where.http.post",
            connected_contract,
        )
