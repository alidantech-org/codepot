"""Tests for template contract models."""

from __future__ import annotations

from tests.fixtures.contracts import make_template_contract


def test_template_contract_has_locked_roots(tmp_path) -> None:
    contract = make_template_contract(tmp_path)

    assert contract.project.name.path.o.original == "test_package"
    assert contract.api.info.title == "Test API"
    assert contract.lang.name == "debug"
    assert contract.emit.output_path == tmp_path
    assert len(contract.schemas.all) == 1
