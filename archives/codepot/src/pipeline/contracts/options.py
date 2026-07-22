"""Pipeline option contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PipelineOptions:
    """User/runtime options for one pipeline execution."""

    spec_path: Path
    template_package_path: Path
    output_path: Path

    language: str | None = None
    select: tuple[str, ...] = ()
    template_ids: tuple[str, ...] = ()

    dry_run: bool = False
    force: bool = False
    debug: bool = False
    verbose: bool = False

    validate_templates: bool = True
    render: bool = True
    write: bool = True
    write_graph: bool = True
