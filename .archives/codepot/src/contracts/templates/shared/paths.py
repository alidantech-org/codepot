"""Template path context contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TemplateOutputPath:
    """One resolved output path for a template render."""

    path: Path
    relative_path: str
    is_barrel: bool = False


@dataclass(frozen=True)
class TemplatePathContext:
    """Path context exposed to template rendering."""

    output: TemplateOutputPath
    template_path: Path
    template_relative_path: str
    output_root: Path


@dataclass(frozen=True)
class TemplatePathVariableContext:
    """Lightweight path variable context used for output path expansion."""

    values: dict[str, object]