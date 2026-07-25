"""Real OpenAPI fixture helpers."""

from __future__ import annotations

from pathlib import Path

from src.inference.engine import InferenceEngine
from src.inference.lossless_contract import build_api_contract
from src.openapi.loader import load_openapi_document


def load_real_graph(path: Path):
    """Load a committed real-world OpenAPI document into the inference graph."""
    document = load_openapi_document(path)
    return InferenceEngine().infer(document)


def load_real_contract(path: Path):
    """Load a committed real-world OpenAPI document into the lossless contract."""
    return build_api_contract(load_real_graph(path))
