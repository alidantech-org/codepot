"""Barrel template context contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from archives.codepot.src.contracts.language.exports import LanguageExport
from archives.codepot.src.contracts.templates.context.base import TemplateBaseContext


@dataclass(frozen=True)
class TemplateBarrelEmittedFileContext:
    """One emitted file available to a barrel template."""

    template_id: str
    output_path: Path
    relative_output_path: str
    symbols: tuple[str, ...]


@dataclass(frozen=True)
class TemplateBarrelContext:
    """Context for a template entry barrel.

    A barrel is not a normal selector. It receives emission/export context from
    its parent template entry.
    """

    base: TemplateBaseContext
    parent_template_id: str
    emitted_files: tuple[TemplateBarrelEmittedFileContext, ...]
    exports: tuple[LanguageExport, ...]
