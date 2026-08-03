"""Bundled JSON Schemas for CodepotG authoring files."""

from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path
from typing import Any

CODEPOTG_SCHEMA_ID = "https://schemas.codepot.dev/codepotg/v1/codepotg.schema.json"
PATHS_SCHEMA_ID = "https://schemas.codepot.dev/codepotg/v1/paths.schema.json"

_SCHEMA_FILES = {
    "codepotg": "codepotg.schema.json",
    "paths": "paths.schema.json",
}


def schema_path(name: str) -> Path:
    """Return the installed path for one bundled authoring schema."""
    try:
        filename = _SCHEMA_FILES[name]
    except KeyError as error:
        supported = ", ".join(sorted(_SCHEMA_FILES))
        raise ValueError(f"Unknown CodepotG schema '{name}'. Supported: {supported}.") from error
    return Path(str(files(__package__).joinpath(filename)))


def load_schema(name: str) -> dict[str, Any]:
    """Load one bundled JSON Schema as a dictionary."""
    return json.loads(schema_path(name).read_text(encoding="utf-8"))


__all__ = [
    "CODEPOTG_SCHEMA_ID",
    "PATHS_SCHEMA_ID",
    "load_schema",
    "schema_path",
]
