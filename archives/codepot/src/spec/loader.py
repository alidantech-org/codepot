"""Public loader for compiled Codepot specs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from archives.codepot.src.spec.ir.shared.document import CodepotDefinition


def load_spec(path: Path) -> CodepotDefinition:
    """Load a compiled Codepot spec file into a typed IR document."""

    with path.open("r", encoding="utf-8") as file:
        loaded: Any = yaml.safe_load(file)

    if not isinstance(loaded, dict):
        raise ValueError(f"Expected spec file to contain an object: {path}")

    return CodepotDefinition.model_validate(loaded)
