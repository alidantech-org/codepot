from __future__ import annotations

from dataclasses import asdict
from typing import Any

from inference.models import InferenceGraph


def inference_graph_to_dict(graph: InferenceGraph) -> dict[str, Any]:
    return asdict(graph)
