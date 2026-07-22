"""Inference graph output serialization."""

from __future__ import annotations

import json
from pathlib import Path

from constants.files import ENCODING_UTF8
from inference.models import InferenceGraph
from inference.serialization import inference_graph_to_dict


def write_inference_graph(graph: InferenceGraph, output_path: Path) -> Path:
    """Write an inference graph as JSON and return the written path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(inference_graph_to_dict(graph), indent=2, default=str),
        encoding=ENCODING_UTF8,
    )
    return output_path
