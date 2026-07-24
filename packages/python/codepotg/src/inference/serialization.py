from __future__ import annotations

from dataclasses import asdict
from typing import Any

from inference.models import InferenceGraph


def inference_graph_to_dict(
    graph: InferenceGraph,
    *,
    include_raw: bool = False,
) -> dict[str, Any]:
    """Serialize inference facts while preserving the established default output."""
    result = asdict(graph)
    if not include_raw:
        result.pop("raw", None)
    return result
