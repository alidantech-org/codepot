from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from codepotg.ir import (
    Contract,
    OperationFacets,
    Schema,
    SchemaKind,
    SchemaUse,
    SemanticId,
    TypeExpression,
    WorkflowStepKind,
)
from codepotg.naming import Name
from codepotg.validation import validate_contract


def test_connected_application_contract_validates(connected_contract: Contract) -> None:
    diagnostics = validate_contract(connected_contract)

    assert not diagnostics.has_errors
    group = connected_contract.groups[0]
    assert group.storage.mappings == group.storage_mappings
    assert group.operations[2].facets.trigger is not None
    assert group.workflows[0].steps[0].compensation is not None
    assert group.workflows[0].steps[1].kind is WorkflowStepKind.END


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
            name=Name("EmptyEnum"),
            kind=SchemaKind.ENUM,
        )

    with pytest.raises(ValueError, match="array schemas require"):
        Schema(
            id=SemanticId("schema.array"),
            name=Name("Users"),
            kind=SchemaKind.ARRAY,
        )

    assert TypeExpression.array_of(TypeExpression.primitive("string")).arguments


def test_missing_schema_reference_fails_before_generation(connected_contract: Contract) -> None:
    group = connected_contract.groups[0]
    operation = group.operations[0]
    broken_operation = replace(
        operation,
        inputs=(
            SchemaUse(
                name=Name("request"),
                schema=SemanticId("missing.schema"),
                required=True,
            ),
        ),
    )
    broken_group = replace(group, operations=(broken_operation, *group.operations[1:]))
    broken_contract = replace(connected_contract, groups=(broken_group,))

    diagnostics = validate_contract(broken_contract)

    assert diagnostics.has_errors
    assert {item.code for item in diagnostics.items} == {"IR_MISSING_SCHEMA"}
    assert diagnostics.items[0].details == (
        ("id", "missing.schema"),
        ("relation", "schema use"),
    )
