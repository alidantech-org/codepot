from __future__ import annotations

from codepotg_openapi.references.graph import ReferenceGraph
from codepotg_openapi.references.identity import ReferenceIdentity


def test_cycle_detection_is_bounded_and_deterministic() -> None:
    graph = ReferenceGraph()
    first = ReferenceIdentity("memory:root", "/components/schemas/First")
    second = ReferenceIdentity("memory:root", "/components/schemas/Second")
    assert graph.add(first, second) is False
    assert graph.add(second, first) is True
    assert graph.add(first, second) is True
