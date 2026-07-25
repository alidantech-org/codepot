from __future__ import annotations

from contracts.source import FrozenMap
from inference.engine import InferenceEngine
from inference.generation_contract import build_generation_contract


def test_generation_contract_skips_unused_normalized_views_without_source_loss() -> None:
    document = {
        "openapi": "3.1.0",
        "info": {"title": "Fast API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "operationId": "listUsers",
                    "responses": {"200": {"description": "OK"}},
                }
            }
        },
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {"id": {"type": "string"}},
                }
            }
        },
        "x-project": {"owner": "codepotg"},
    }

    contract = build_generation_contract(
        InferenceEngine().infer(document),
        normalized_roots=(),
    )

    assert contract.info.title == "Fast API"
    assert contract.operations[0].id == "listUsers"
    assert contract.schemas.by_id["User"].id == "User"
    assert isinstance(contract.raw, FrozenMap)
    assert contract.raw["components"]["schemas"]["User"]["type"] == "object"
    assert contract.extensions["x-project"]["owner"] == "codepotg"
    assert contract.meta["normalized_roots"] == ()
    assert "normalized" not in contract.meta
    assert "normalized_domains" not in contract.meta
    assert "normalized_schemas" not in contract.meta
    assert contract.meta["loss_count"] == 0
