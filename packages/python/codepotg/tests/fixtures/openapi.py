"""Real OpenAPI fixture helpers."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from src.inference.engine import InferenceEngine
from src.inference.lossless_contract import build_api_contract
from src.openapi.loader import load_openapi_document


@lru_cache(maxsize=4)
def load_real_graph(path: Path):
    """Load one committed real-world OpenAPI document per test session."""
    document = load_openapi_document(path)
    return InferenceEngine().infer(document)


@lru_cache(maxsize=4)
def load_real_contract(path: Path):
    """Build one cached lossless contract per committed fixture format."""
    return build_api_contract(load_real_graph(path))
