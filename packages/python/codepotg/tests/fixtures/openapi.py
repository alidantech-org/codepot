"""OpenAPI fixture helpers."""

from __future__ import annotations

from pathlib import Path

from src.inference.engine import InferenceEngine
from src.openapi.loader import load_openapi_document


def load_sample_graph(path: Path):
    """Load a sample OpenAPI document and return an inference graph."""
    document = load_openapi_document(path)
    return InferenceEngine().infer(document)
