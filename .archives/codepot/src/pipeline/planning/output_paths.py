"""Filesystem-based output path construction."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from archives.codepot.src.pipeline.planning.path_debug import PathPlanningDebug
from archives.codepot.src.pipeline.planning.path_expander import (
    expand_path_parts,
    join_expanded_path,
)
from archives.codepot.src.pipeline.planning.path_variables import OutputPathVariables
from archives.codepot.src.pipeline.planning.template_files import DiscoveredTemplateFile


@dataclass(frozen=True)
class BuiltOutputPath:
    """Built output path with debug metadata."""

    output_path: Path
    debug: PathPlanningDebug


def _has_variable(text: str) -> bool:
    """Return true when a text segment appears to contain a path variable."""

    return "[" in text or "]" in text


def _validate_literal_folder_segments(template_file: DiscoveredTemplateFile) -> None:
    """Reject path variables inside filesystem folder segments."""

    folder_parts = template_file.output_relative_path.parent.parts

    for part in folder_parts:
        if _has_variable(part):
            raise ValueError(
                "Filesystem folder segments must not contain path variables. "
                f"Move folder variable '{part}' into codepotx.yaml folders for "
                f"template '{template_file.template_id}'."
            )


def _filesystem_file(template_file: DiscoveredTemplateFile) -> str:
    """Return output file name from the template file path."""

    return template_file.output_relative_path.name


def _merged_folders(
    *,
    template_file: DiscoveredTemplateFile,
    configured_folders: tuple[str, ...],
) -> tuple[str, ...]:
    """Insert configured folders where the {key} segment was removed."""

    if not configured_folders:
        return tuple(template_file.output_relative_path.parent.parts)

    marker = f"{{{template_file.template_id}}}"
    original_parts = template_file.relative_path.parent.parts

    merged: list[str] = []

    for part in original_parts:
        if part == marker:
            merged.extend(configured_folders)
            continue

        merged.append(part)

    return tuple(merged)


def build_output_path(
    *,
    output_root: Path,
    template_file: DiscoveredTemplateFile,
    configured_folders: tuple[str, ...],
    variables: OutputPathVariables,
) -> BuiltOutputPath:
    """Build final output path from filesystem path and config folders."""

    _validate_literal_folder_segments(template_file)

    original_folders = _merged_folders(
        template_file=template_file,
        configured_folders=configured_folders,
    )
    original_file = _filesystem_file(template_file)

    try:
        folder_result = expand_path_parts(original_folders, variables)
        file_result = expand_path_parts((original_file,), variables)
    except ValueError as error:
        raise ValueError(
            f"Failed to expand output path for template file "
            f"'{template_file.relative_template_path}': {error}"
        ) from error

    if len(file_result.parts) != 1:
        raise ValueError(
            "Output file name did not expand to one safe file segment: "
            f"{original_file}"
        )

    output_path = join_expanded_path(
        output_root=output_root,
        folders=folder_result.parts,
        file=file_result.parts[0],
    )

    debug = PathPlanningDebug(
        template_id=template_file.template_id,
        source_key=None,
        original_folders=original_folders,
        original_file=original_file,
        expanded_folders=tuple(part.value for part in folder_result.parts),
        expanded_file=file_result.parts[0].value,
        variable_reads=folder_result.reads + file_result.reads,
        owner_key=variables.owner.key if variables.owner is not None else None,
        owner_folders=variables.owner.folders if variables.owner is not None else (),
    )

    return BuiltOutputPath(
        output_path=output_path,
        debug=debug,
    )