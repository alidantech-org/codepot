"""YAML file loading utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_yaml_file(path: Path) -> dict[str, Any]:
    """Load a YAML file as an object."""

    with path.open("r", encoding="utf-8") as file:
        loaded: Any = yaml.safe_load(file)

    if not isinstance(loaded, dict):
        raise ValueError(f"Expected YAML object in file: {path}")

    return loaded
