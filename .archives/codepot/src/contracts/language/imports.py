"""File-level import contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class LanguageImportKind(StrEnum):
    """Kinds of language imports."""

    STANDARD = "standard"
    LOCAL = "local"
    RELATIVE = "relative"
    ALIAS = "alias"
    PACKAGE = "package"


@dataclass(frozen=True)
class LanguageImportSymbol:
    """One imported symbol."""

    name: str
    alias: str | None = None
    is_type_only: bool = False


@dataclass(frozen=True)
class LanguageImport:
    """One file-level import prepared by the language import planner."""

    kind: LanguageImportKind
    module: str
    symbols: tuple[LanguageImportSymbol, ...]
    rendered: str
    source_path: Path | None = None
    target_path: Path | None = None
    is_type_only: bool = False
