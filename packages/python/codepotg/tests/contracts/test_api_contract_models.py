"""Tests for API contract models."""

from __future__ import annotations

from tests.fixtures.contracts import make_api_contract


def test_api_contract_contains_stable_api_facts() -> None:
    api = make_api_contract()

    assert api.info.title == "Test API"
    assert api.info.openapi_version == "3.1.0"
    assert api.servers[0].url == "https://api.example.test"
    assert api.resources[0].name.path.original == "users"
    assert api.schemas.all[0].kind == "model"
    assert api.operations[0].method == "get"
