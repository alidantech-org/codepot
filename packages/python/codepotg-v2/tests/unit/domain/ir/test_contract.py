from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from codepotg.ir import Contract, OperationFacets, Schema, SchemaKind, SemanticId, TypeExpression


def test_connected_application_contract_exposes_expected_relations(
    connected_contract: Contract,
) -> None:
    group = connected_contract.groups[0]

    assert group.storage.mappings == group.storage_mappings
    assert group.operations[2].facets.trigger is not None
    assert group.workflows[0].steps[0].compensation is not None


def test_kernel_objects_are_immutable(connected_contract: Contract) -> None:
    with pytest.raises(FrozenInstanceError):
        connected_contract.version = "changed"  # type: ignore[misc]


def test_closed_facets_reject_unknown_semantic_extensions() -> None:
    with pytest.raises(TypeError):
        OperationFacets(billing=object())  # type: ignore[call-arg]


def test_structural_schema_kinds_enforce_required_shape() -> None:
    with pytest.raises(ValueError, match="enum schemas require"):
        Schema(
            id=SemanticId("schema.empty_enum"),
            name=connected_name("EmptyEnum"),
            kind=SchemaKind.ENUM,
        )

    with pytest.raises(ValueError, match="array schemas require"):
        Schema(
            id=SemanticId("schema.array"),
            name=connected_name("Users"),
            kind=SchemaKind.ARRAY,
        )

    assert TypeExpression.array_of(TypeExpression.primitive("string")).arguments


def connected_name(value: str):
    from codepotg.ir import Name

    return Name(value)
