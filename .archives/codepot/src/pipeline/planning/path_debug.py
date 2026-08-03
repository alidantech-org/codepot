"""Output path planning debug models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PathVariableRead:
    """One output path variable read."""

    variable: str
    value: str


@dataclass(frozen=True)
class PathPlanningDebug:
    """Debug metadata for one planned output path."""

    template_id: str
    source_key: str | None

    original_folders: tuple[str, ...]
    original_file: str

    expanded_folders: tuple[str, ...]
    expanded_file: str

    variable_reads: tuple[PathVariableRead, ...]

    owner_key: str | None = None
    owner_folders: tuple[str, ...] = ()