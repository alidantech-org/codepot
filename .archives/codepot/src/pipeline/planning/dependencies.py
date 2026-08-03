"""Emission dependency planning models and helpers."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.contracts.spec.dependencies import SpecDependency
from archives.codepot.src.contracts.spec.records import SpecRecord
from archives.codepot.src.pipeline.planning.files import PlannedOutputFile


@dataclass(frozen=True)
class PlannedFileDependency:
    """One dependency attached to a planned output file."""

    file_id: str
    source_record: SpecRecord[object]
    dependency: SpecDependency


@dataclass(frozen=True)
class PlannedFileDependencies:
    """All planned dependencies for output files."""

    items: tuple[PlannedFileDependency, ...]


def plan_file_dependencies(
    files: tuple[PlannedOutputFile, ...],
) -> PlannedFileDependencies:
    """Collect dependencies from records included in planned files."""

    dependencies: list[PlannedFileDependency] = []

    for file in files:
        for record in file.source.records:
            for dependency in record.dependencies:
                dependencies.append(
                    PlannedFileDependency(
                        file_id=file.id,
                        source_record=record,
                        dependency=dependency,
                    )
                )

    return PlannedFileDependencies(items=tuple(dependencies))
