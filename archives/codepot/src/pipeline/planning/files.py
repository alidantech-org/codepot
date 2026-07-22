"""Planned output file models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from archives.codepot.src.contracts.spec.records import SpecRecord
from archives.codepot.src.contracts.templates.config.selection import TemplateSelect
from archives.codepot.src.contracts.templates.config.template import TemplateEntryConfig
from archives.codepot.src.pipeline.planning.path_debug import PathPlanningDebug


@dataclass(frozen=True)
class PlannedOutputSource:
    """Source data used to create one planned output file."""

    records: tuple[SpecRecord[object], ...]
    bucket_key: str | None = None


@dataclass(frozen=True)
class PlannedOutputFile:
    """One file planned for emission."""

    id: str
    template_id: str
    template: TemplateEntryConfig
    select: TemplateSelect

    output_path: Path
    relative_output_path: str

    source: PlannedOutputSource
    is_barrel: bool = False
    parent_template_id: str | None = None
    path_debug: PathPlanningDebug | None = None

    template_file: str | None = None
    source_template_path: Path | None = None

    is_static: bool = False
    render_once: bool = False
    barrel_source_file_ids: tuple[str, ...] = ()