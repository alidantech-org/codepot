"""Lossless enrichment for the stable inference-to-API contract boundary."""

from __future__ import annotations

from dataclasses import replace

from contracts.api import ApiContract
from contracts.source import freeze_source_map
from inference.contract import build_api_contract as build_normalized_api_contract
from inference.models import InferenceGraph


def build_api_contract(graph: InferenceGraph) -> ApiContract:
    """Build the existing normalized contract and add immutable source views."""
    contract = build_normalized_api_contract(graph)
    extensions = {
        str(key): value
        for key, value in graph.raw.items()
        if isinstance(key, str) and key.startswith("x-")
    }
    return replace(
        contract,
        raw=freeze_source_map(graph.raw),
        extensions=freeze_source_map(extensions),
    )
