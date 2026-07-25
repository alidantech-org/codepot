from __future__ import annotations

from pathlib import Path

import pytest

from contracts.source import FrozenMap
from inference.engine import InferenceEngine
from inference.lossless_contract import build_api_contract
from inference.serialization import inference_graph_to_dict
from openapi.loader import load_openapi_document


def test_api_contract_exposes_complete_immutable_root_source() -> None:
    document = load_openapi_document(_fixture_path())
    graph = InferenceEngine().infer(document)
    contract = build_api_contract(graph)

    assert isinstance(contract.raw, FrozenMap)
    assert contract.raw["openapi"] == "3.1.0"
    assert contract.raw["info"]["title"] == "CodepotG Fixture API"
    assert contract.raw["paths"]["/users"]["get"]["operationId"] == "listUsers"
    assert contract.raw["components"]["schemas"]["UserModel"]["properties"]["age"]["default"] == 18
    assert contract.raw.to_dict() == document.raw

    with pytest.raises(TypeError):
        contract.raw["new"] = "value"  # type: ignore[index]

    with pytest.raises(TypeError):
        contract.raw["info"]["title"] = "Changed"  # type: ignore[index]

    assert contract.raw["servers"] == (FrozenMap({"url": "https://fixture.example.test"}),)


def test_api_contract_exposes_root_extensions_without_removing_meta() -> None:
    document = load_openapi_document(_fixture_path())
    graph = InferenceEngine().infer(document)
    contract = build_api_contract(graph)

    extension = contract.extensions["x-fixture"]
    assert extension["owner"] == "codepotg"
    assert extension["enabled"] is True
    assert extension["values"] == ("first", "second")
    assert "explicitNull" in extension
    assert extension["explicitNull"] is None
    assert contract.meta["x-codegen"] == {}


def test_inference_graph_owns_a_deep_copy_of_the_document() -> None:
    document = load_openapi_document(_fixture_path())
    graph = InferenceEngine().infer(document)

    document.raw["info"]["title"] = "Mutated after inference"
    document.raw["paths"]["/users"]["get"]["operationId"] = "mutatedOperation"

    assert graph.raw["info"]["title"] == "CodepotG Fixture API"
    assert graph.raw["paths"]["/users"]["get"]["operationId"] == "listUsers"


def test_inference_serialization_preserves_existing_default_and_allows_raw_opt_in() -> None:
    document = load_openapi_document(_fixture_path())
    graph = InferenceEngine().infer(document)

    default_output = inference_graph_to_dict(graph)
    lossless_output = inference_graph_to_dict(graph, include_raw=True)

    assert "raw" not in default_output
    assert lossless_output["raw"] == document.raw


def _fixture_path() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "project_openapi.yaml"
