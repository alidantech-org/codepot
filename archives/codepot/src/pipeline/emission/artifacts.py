"""Emission artifact writing helpers."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from archives.codepot.src.pipeline.emission.graph import EmissionGraph

EMISSION_ARTIFACT_DIR = ".codepotx"
EMISSION_GRAPH_FILE = "emission.graph.json"


def _to_jsonable(value: Any) -> Any:
    """Convert emission artifact values into JSON-compatible data."""

    if is_dataclass(value) and not isinstance(value, type):
        return {
            key: _to_jsonable(item)
            for key, item in asdict(value).items()
        }

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, Path):
        return value.as_posix()

    if isinstance(value, tuple | list):
        return [_to_jsonable(item) for item in value]

    if isinstance(value, dict):
        return {
            str(key): _to_jsonable(item)
            for key, item in value.items()
        }

    if isinstance(value, str | int | float | bool) or value is None:
        return value

    return str(value)


def emission_graph_path(output_root: Path) -> Path:
    """Return the default emission graph artifact path."""

    return output_root / EMISSION_ARTIFACT_DIR / EMISSION_GRAPH_FILE


def write_emission_graph(
    *,
    output_root: Path,
    graph: EmissionGraph,
    dry_run: bool,
) -> Path:
    """Write the emission graph artifact unless this is a dry run."""

    path = emission_graph_path(output_root)

    if dry_run:
        return path

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_to_jsonable(graph), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    return path
