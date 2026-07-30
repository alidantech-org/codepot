from __future__ import annotations

from dataclasses import replace

from dryv.ir import Contract, Name, SchemaUse, SemanticId, validate_contract


def test_connected_contract_validates(connected_contract: Contract) -> None:
    diagnostics = validate_contract(connected_contract)

    assert not diagnostics.has_errors


def test_missing_schema_reference_fails_before_generation(
    connected_contract: Contract,
) -> None:
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
