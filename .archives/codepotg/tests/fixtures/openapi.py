"""Real OpenAPI fixture helpers."""

from __future__ import annotations

from pathlib import Path

from archives.codepotg.src.inference.engine import InferenceEngine
from archives.codepotg.src.inference.lossless_contract import build_api_contract
from archives.codepotg.src.openapi.loader import load_openapi_document


def load_real_graph(path: Path):
    """Load a committed real-world OpenAPI document into an inference graph."""
    document = load_openapi_document(path)
    return InferenceEngine().infer(document)


def load_real_contract(path: Path):
    """Build a lossless contract without retaining the intermediate graph."""
    document = load_openapi_document(path)
    graph = InferenceEngine().infer(document, copy_raw=False)
    return build_api_contract(graph)
