"""JSON output helpers."""

from __future__ import annotations

import dataclasses
import json
from typing import Any

from archives.codepot.src.cli.presentation.console import console


def print_json_result(result: Any) -> None:
    if hasattr(result, "model_dump"):
        payload = result.model_dump(mode="json")
    elif dataclasses.is_dataclass(result):
        payload = dataclasses.asdict(result)
    else:
        payload = result
    console.print(json.dumps(payload, indent=2, sort_keys=True))
