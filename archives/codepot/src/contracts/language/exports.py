"""File-level export contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class LanguageExportStrategy(StrEnum):
    """Supported export strategies."""

    NAMED = "named"
    STAR = "star"


@dataclass(frozen=True)
class LanguageExportSymbol:
    """One exported symbol."""

    name: str
    alias: str | None = None


@dataclass(frozen=True)
class LanguageExport:
    """One file-level export prepared by the language export planner."""

    strategy: LanguageExportStrategy
    module: str
    symbols: tuple[LanguageExportSymbol, ...]
    rendered: str
    source_path: Path | None = None
    target_path: Path | None = None
