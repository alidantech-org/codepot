"""Tests for emission engine orchestration."""

from __future__ import annotations

from tests.fixtures.contracts import make_template_contract
from tests.fixtures.templates import write_debug_templates


def test_emission_engine_processes_template_contract(tmp_path) -> None:
    template_root = write_debug_templates(tmp_path)
    contract = make_template_contract(tmp_path, template_root)

    assert contract.emit.output_path == tmp_path
    assert contract.emit.template_root == template_root
    assert len(contract.schemas.all) == 1
