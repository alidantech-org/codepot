"""Emission graph models and builders."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from archives.codepot.src.pipeline.contracts.results import PipelineReport
from archives.codepot.src.pipeline.emission.writer import FileWriteStatus
from archives.codepot.src.pipeline.planning.contexts import PlannedTemplateContexts
from archives.codepot.src.pipeline.planning.files import PlannedOutputFile


@dataclass(frozen=True)
class EmissionGraphFile:
    """One emitted/planned file in the emission graph."""

    file_id: str
    template_id: str
    output_path: str
    records: tuple[str, ...]
    write_status: FileWriteStatus | None = None
    owner_key: str | None = None
    owner_folders: tuple[str, ...] = ()
    expanded_folders: tuple[str, ...] = ()
    expanded_file: str | None = None
    is_barrel: bool = False
    is_static: bool = False
    render_once: bool = False
    parent_template_id: str | None = None
    barrel_source_file_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class EmissionGraphTemplate:
    """One template entry in the emission graph."""

    template_id: str
    select: str
    files: tuple[str, ...]


@dataclass(frozen=True)
class EmissionGraph:
    """Emission graph artifact for one pipeline run."""

    spec_hash: str
    project_key: str
    project_version: str
    language: str
    output_root: str
    templates: tuple[EmissionGraphTemplate, ...]
    files: tuple[EmissionGraphFile, ...]
    report: PipelineReport


def _write_status_for_file(
    *,
    file_id: str,
    state_write_results,
) -> FileWriteStatus | None:
    """Return write status for a file when write results exist."""

    if state_write_results is None:
        return None

    for result in state_write_results.files:
        if result.file_id == file_id:
            return result.status

    return None


def _graph_file(
    *,
    file: PlannedOutputFile,
    write_results,
) -> EmissionGraphFile:
    """Create one graph file record."""

    debug = file.path_debug

    return EmissionGraphFile(
        file_id=file.id,
        template_id=file.template_id,
        output_path=file.relative_output_path,
        records=tuple(record.id for record in file.source.records),
        write_status=_write_status_for_file(
            file_id=file.id,
            state_write_results=write_results,
        ),
        owner_key=debug.owner_key if debug else None,
        owner_folders=debug.owner_folders if debug else (),
        expanded_folders=debug.expanded_folders if debug else (),
        expanded_file=debug.expanded_file if debug else None,
        is_barrel=file.is_barrel,
        is_static=file.is_static,
        render_once=file.render_once,
        parent_template_id=file.parent_template_id,
        barrel_source_file_ids=file.barrel_source_file_ids,
    )


def _graph_templates(
    files: tuple[PlannedOutputFile, ...],
) -> tuple[EmissionGraphTemplate, ...]:
    """Create template graph records from planned files."""

    grouped: dict[str, list[PlannedOutputFile]] = {}

    for file in files:
        grouped.setdefault(file.template_id, []).append(file)

    templates: list[EmissionGraphTemplate] = []

    for template_id, template_files in sorted(
        grouped.items(), key=lambda item: item[0]
    ):
        first_file = template_files[0]
        templates.append(
            EmissionGraphTemplate(
                template_id=template_id,
                select=first_file.select.raw,
                files=tuple(file.id for file in template_files),
            )
        )

    return tuple(templates)


def build_emission_graph(
    *,
    output_root: Path,
    contexts: PlannedTemplateContexts,
    files: tuple[PlannedOutputFile, ...],
    write_results,
    report: PipelineReport,
) -> EmissionGraph:
    """Build an emission graph artifact."""

    spec = contexts.files[0].spec if contexts.files else None
    language = contexts.files[0].language if contexts.files else None

    if spec is None:
        raise ValueError("Cannot build emission graph without spec context.")

    if language is None:
        raise ValueError("Cannot build emission graph without language runtime.")

    return EmissionGraph(
        spec_hash=spec.metadata.file.hash,
        project_key=spec.metadata.project.project_key,
        project_version=str(spec.metadata.project.version),
        language=language.name,
        output_root=output_root.as_posix(),
        templates=_graph_templates(files),
        files=tuple(
            _graph_file(
                file=file,
                write_results=write_results,
            )
            for file in files
        ),
        report=report,
    )