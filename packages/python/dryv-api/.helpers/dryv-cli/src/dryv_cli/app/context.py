from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dryv_cli.presentation import Console


@dataclass(frozen=True, slots=True)
class AppContext:
    start: Path
    api_url: str | None
    console: Console


__all__ = ["AppContext"]
