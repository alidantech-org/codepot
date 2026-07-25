"""Generation-specific contract construction with a compatibility-safe fast path."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import replace
from typing import Any

from contracts.source import freeze_source_map
from inference.contract import build_api_contract as build_compatibility_api_contract
from inference.lossless_contract import build_api_contract as build_full_api_contract
from inference.models import InferenceGraph


def build_generation_contract(
    graph: InferenceGraph,
    *,
    normalized_roots: Iterable[str],
):
    """Build only the compatibility contract when no normalized root is consumed.

    The complete historical lossless contract remains the fallback whenever a pack
    references any normalized root. This keeps public API behavior unchanged while
    removing the largest avoidable construction cost from compatibility-only packs.
    """
    requested = frozenset(str(value) for value in normalized_roots)
    if requested or _requires_entity_bridge(graph.raw):
        return build_full_api_contract(graph)

    contract = build_compatibility_api_contract(graph)
    raw = graph.raw or {}
    extensions = {
        str(key): value
        for key, value in raw.items()
        if isinstance(key, str) and key.startswith("x-")
    }
    return replace(
        contract,
        raw=freeze_source_map(raw),
        extensions=freeze_source_map(extensions),
        meta={
            **contract.meta,
            "normalized_roots": (),
            "loss_count": 0,
            "unresolved_count": 0,
            "cycle_count": 0,
            "raw_only_count": 0,
        },
    )


def _requires_entity_bridge(raw: Mapping[str, Any] | None) -> bool:
    if not isinstance(raw, Mapping):
        return False
    codegen = raw.get("x-codegen")
    if not isinstance(codegen, Mapping):
        return False
    entities = codegen.get("entities")
    if not isinstance(entities, Mapping):
        return False
    return any(
        isinstance(value, Mapping) and bool(_FLAT_ENTITY_KEYS.intersection(value))
        for value in entities.values()
    )


_FLAT_ENTITY_KEYS = {
    "resource",
    "schema",
    "store",
    "table",
    "kind",
    "abstract",
    "visibility",
    "extends",
    "fields",
    "backendFields",
    "backend",
    "relations",
    "constraints",
    "indexes",
    "unique",
    "info",
    "notes",
}
