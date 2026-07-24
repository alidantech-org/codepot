from __future__ import annotations

from dataclasses import asdict, replace
from typing import Any

from inference.models import InferenceGraph


def inference_graph_to_dict(
    graph: InferenceGraph,
    *,
    include_raw: bool = False,
) -> dict[str, Any]:
    """Serialize inference facts while preserving the established default output."""
    serializable_graph = graph if include_raw else replace(graph, raw={})
    result = asdict(serializable_graph)
    if not include_raw:
        result.pop("raw", None)
    return result
