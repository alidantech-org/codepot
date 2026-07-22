"""Import planner contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from contracts.template import TemplateDependency, TemplateFile, TemplateImport


@dataclass(frozen=True)
class ImportPlanningContext:
    """Context passed to language import planners."""

    current_file: TemplateFile
    dependencies: tuple[TemplateDependency, ...]
    strategy: str
    output_root: Path | None = None
    package_name: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)


class ImportPlanner(Protocol):
    """Language-specific import/link planner."""

    def plan_imports(self, context: ImportPlanningContext) -> tuple[TemplateImport, ...]:
        """Build template-ready import objects."""
        ...
