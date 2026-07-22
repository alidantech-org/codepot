"""Template dependency context contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from archives.codepot.src.contracts.spec.dependencies import SpecDependency
from archives.codepot.src.contracts.spec.refs import SpecRef


class TemplateDependencyResolution(StrEnum):
    """How a dependency was resolved for a planned template file."""

    SAME_FILE = "same_file"
    DIRECT_FILE = "direct_file"
    BARREL = "barrel"
    EXTERNAL = "external"
    MISSING = "missing"


@dataclass(frozen=True)
class TemplateDependencyTarget:
    """Resolved dependency target for template rendering/import planning."""

    ref: SpecRef
    subject: str
    symbol: str | None = None
    output_path: Path | None = None
    template_id: str | None = None
    uses_barrel: bool = False


@dataclass(frozen=True)
class TemplateDependency:
    """Template-facing dependency item."""

    spec: SpecDependency
    resolution: TemplateDependencyResolution
    target: TemplateDependencyTarget | None = None


@dataclass(frozen=True)
class TemplateDependencyGroup:
    """Dependencies grouped by subject."""

    subject: str
    items: tuple[TemplateDependency, ...]


@dataclass(frozen=True)
class TemplateDependencies:
    """All dependencies available to one template file."""

    groups: tuple[TemplateDependencyGroup, ...]
    missing: tuple[TemplateDependency, ...] = ()
    external: tuple[TemplateDependency, ...] = ()