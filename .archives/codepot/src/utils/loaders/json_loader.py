"""JSON file loading utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json_file(path: Path) -> dict[str, Any]:
    """Load a JSON file as an object."""

    with path.open("r", encoding="utf-8") as file:
        loaded: Any = json.load(file)

    if not isinstance(loaded, dict):
        raise ValueError(f"Expected JSON object in file: {path}")

    return loaded
