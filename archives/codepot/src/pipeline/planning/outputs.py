"""Output file planning orchestration."""

from __future__ import annotations

from pathlib import Path

from archives.codepot.src.contracts.language.runtime import LanguageRuntime
from archives.codepot.src.contracts.spec.context import SpecContext
from archives.codepot.src.contracts.spec.records import SpecRecord
from archives.codepot.src.contracts.templates.config.package import LoadedTemplatePackageConfig
from archives.codepot.src.contracts.templates.config.selection import TemplateSelect, TemplateSelectMode
from archives.codepot.src.contracts.templates.config.template import TemplateEntryConfig
from archives.codepot.src.pipeline.planning.files import PlannedOutputFile, PlannedOutputSource
from archives.codepot.src.pipeline.planning.output_paths import build_output_path
from archives.codepot.src.pipeline.planning.path_variables import (
    OutputPathVariables,
    PathGlobalVariables,
    PathProjectVariables,
    global_owner_variables,
    item_variables,
    language_variables,
    owner_variables,
    owner_variables_from_key_with_folders,
    template_variables,
)
from archives.codepot.src.pipeline.planning.selections import PlannedSelection
from archives.codepot.src.pipeline.planning.template_files import (
    DiscoveredTemplateFile,
    TemplateFileRole,
    discover_template_files,
)
from archives.codepot.src.spec.utils.constants import GLOBAL_OWNER_KEY


def _relative_output_path(
    *,
    output_root: Path,
    output_path: Path,
) -> str:
    """Return POSIX relative output path."""

    return output_path.relative_to(output_root).as_posix()


def _file_id(
    *,
    template_id: str,
    index: int,
    role: TemplateFileRole,
    bucket_key: str | None = None,
    record: SpecRecord[object] | None = None,
) -> str:
    """Create deterministic planned file id."""

    if record is not None:
        return f"file.{template_id}.{role.value}.{record.id}"

    if bucket_key is not None:
        return f"file.{template_id}.{role.value}.bucket.{bucket_key}"

    return f"file.{template_id}.{role.value}.{index}"


def _sources_for_selection(
    selection: PlannedSelection,
) -> tuple[PlannedOutputSource, ...]:
    """Create output sources for one selection."""

    if selection.select.mode == TemplateSelectMode.ONCE:
        return (PlannedOutputSource(records=()),)

    if selection.select.mode == TemplateSelectMode.ALL:
        return (PlannedOutputSource(records=selection.records),)

    if selection.select.mode == TemplateSelectMode.EACH:
        return tuple(
            PlannedOutputSource(records=(record,)) for record in selection.records
        )

    if selection.select.mode == TemplateSelectMode.BY_OWNER:
        return tuple(
            PlannedOutputSource(
                records=bucket.records,
                bucket_key=bucket.key,
            )
            for bucket in selection.buckets
        )

    raise ValueError(f"Unsupported selection mode: {selection.select.mode}")


def _barrel_sources_for_selection(
    selection: PlannedSelection,
) -> tuple[PlannedOutputSource, ...]:
    """Create grouped barrel sources for one selection."""

    if selection.select.mode == TemplateSelectMode.BY_OWNER:
        return tuple(
            PlannedOutputSource(records=bucket.records, bucket_key=bucket.key)
            for bucket in selection.buckets
        )

    if selection.select.mode == TemplateSelectMode.EACH:
        # each files are barrel-grouped by owner
        grouped: dict[str, list[SpecRecord[object]]] = {}

        for record in selection.records:
            grouped.setdefault(record.owner.key, []).append(record)

        return tuple(
            PlannedOutputSource(records=tuple(records), bucket_key=owner_key)
            for owner_key, records in sorted(grouped.items(), key=lambda item: item[0])
        )

    if selection.select.mode == TemplateSelectMode.ALL:
        return (PlannedOutputSource(records=selection.records),)

    if selection.select.mode == TemplateSelectMode.ONCE:
        return (PlannedOutputSource(records=()),)

    raise ValueError(f"Unsupported barrel selection mode: {selection.select.mode}")


def _owner_from_source(
    *,
    source: PlannedOutputSource,
    template_package: LoadedTemplatePackageConfig,
):
    """Create owner variables from source records or bucket."""

    first_record = source.records[0] if source.records else None
    record_owner = owner_variables(first_record) if first_record is not None else None

    if record_owner is not None:
        owner = record_owner
    elif source.bucket_key is not None:
        owner = owner_variables_from_key_with_folders(source.bucket_key, ())
    else:
        owner = None

    if owner is not None and owner.key == GLOBAL_OWNER_KEY:
        return global_owner_variables(
            alias=template_package.config.defaults.global_alias,
            folders=template_package.config.defaults.global_folders,
        )

    return owner


def _path_variables(
    *,
    selection: PlannedSelection,
    source: PlannedOutputSource,
    runtime: LanguageRuntime,
    spec_context: SpecContext,
    template_package: LoadedTemplatePackageConfig,
) -> OutputPathVariables:
    """Create lightweight typed output path variables."""

    first_record = source.records[0] if source.records else None

    return OutputPathVariables(
        global_context=PathGlobalVariables(
            alias=template_package.config.defaults.global_alias,
            output_root=template_package.package_path,
        ),
        project=PathProjectVariables(
            key=spec_context.metadata.project.project_key,
            version=str(spec_context.metadata.project.version),
            title=spec_context.metadata.project.title,
        ),
        language=language_variables(runtime),
        template=template_variables(selection),
        item=item_variables(first_record) if first_record is not None else None,
        owner=_owner_from_source(
            source=source,
            template_package=template_package,
        ),
    )


def _configured_file(
    *,
    template_file: DiscoveredTemplateFile,
    selection: PlannedSelection,
    source: PlannedOutputSource,
    output_root: Path,
    index: int,
    runtime: LanguageRuntime,
    spec_context: SpecContext,
    template_package: LoadedTemplatePackageConfig,
) -> PlannedOutputFile:
    """Plan one configured dynamic template file."""

    variables = _path_variables(
        selection=selection,
        source=source,
        runtime=runtime,
        spec_context=spec_context,
        template_package=template_package,
    )

    built = build_output_path(
        output_root=output_root,
        template_file=template_file,
        configured_folders=selection.template.folders,
        variables=variables,
    )

    record = source.records[0] if len(source.records) == 1 else None

    return PlannedOutputFile(
        id=_file_id(
            template_id=selection.template_id,
            index=index,
            role=template_file.role,
            bucket_key=source.bucket_key,
            record=record,
        ),
        template_id=selection.template_id,
        template=selection.template,
        select=selection.select,
        output_path=built.output_path,
        relative_output_path=_relative_output_path(
            output_root=output_root,
            output_path=built.output_path,
        ),
        source=source,
        is_barrel=template_file.role == TemplateFileRole.BARREL,
        parent_template_id=(
            selection.template_id
            if template_file.role == TemplateFileRole.BARREL
            else None
        ),
        path_debug=built.debug,
        template_file=template_file.relative_template_path,
        source_template_path=template_file.absolute_path,
        render_once=False,
    )


def _passthrough_file(
    *,
    template_file: DiscoveredTemplateFile,
    output_root: Path,
    index: int,
    runtime: LanguageRuntime,
    spec_context: SpecContext,
    template_package: LoadedTemplatePackageConfig,
) -> PlannedOutputFile:
    """Plan one non-configured filesystem file."""

    select = TemplateSelect(
        raw="once",
        subject=None,
        mode=TemplateSelectMode.ONCE,
    )

    selection = PlannedSelection(
        template_id=template_file.template_id,
        template=TemplateEntryConfig(select="once"),
        select=select,
        records=(),
    )
    source = PlannedOutputSource(records=())
    variables = _path_variables(
        selection=selection,
        source=source,
        runtime=runtime,
        spec_context=spec_context,
        template_package=template_package,
    )

    built = build_output_path(
        output_root=output_root,
        template_file=template_file,
        configured_folders=(),
        variables=variables,
    )

    return PlannedOutputFile(
        id=f"file.once.{index}",
        template_id=template_file.template_id,
        template=selection.template,
        select=selection.select,
        output_path=built.output_path,
        relative_output_path=_relative_output_path(
            output_root=output_root,
            output_path=built.output_path,
        ),
        source=source,
        path_debug=built.debug,
        template_file=template_file.relative_template_path
        if template_file.role == TemplateFileRole.RENDER_ONCE
        else None,
        source_template_path=template_file.absolute_path,
        is_static=template_file.role == TemplateFileRole.STATIC,
        render_once=template_file.role == TemplateFileRole.RENDER_ONCE,
    )


def _selection_by_id(
    selections: tuple[PlannedSelection, ...],
) -> dict[str, PlannedSelection]:
    """Index selections by template id."""

    return {selection.template_id: selection for selection in selections}


def plan_output_files(
    *,
    selections: tuple[PlannedSelection, ...],
    output_root: Path,
    runtime: LanguageRuntime,
    spec_context: SpecContext,
    template_package: LoadedTemplatePackageConfig,
) -> tuple[PlannedOutputFile, ...]:
    """Plan output files from filesystem template files and config keys."""

    files: list[PlannedOutputFile] = []
    selections_by_id = _selection_by_id(selections)

    template_files = discover_template_files(
        package_path=template_package.package_path,
        config=template_package.config,
    )

    for template_file in template_files:
        if template_file.role in {TemplateFileRole.STATIC, TemplateFileRole.RENDER_ONCE}:
            files.append(
                _passthrough_file(
                    template_file=template_file,
                    output_root=output_root,
                    index=len(files),
                    runtime=runtime,
                    spec_context=spec_context,
                    template_package=template_package,
                )
            )
            continue

        selection = selections_by_id.get(template_file.template_id)
        if selection is None:
            raise ValueError(
                f"Template file uses unknown config key: {template_file.template_id}"
            )

        if template_file.role == TemplateFileRole.BARREL:
            if not selection.template.barrel_enabled:
                continue

            for source in _barrel_sources_for_selection(selection):
                files.append(
                    _configured_file(
                        template_file=template_file,
                        selection=selection,
                        source=source,
                        output_root=output_root,
                        index=len(files),
                        runtime=runtime,
                        spec_context=spec_context,
                        template_package=template_package,
                    )
                )
            continue

        for source in _sources_for_selection(selection):
            files.append(
                _configured_file(
                    template_file=template_file,
                    selection=selection,
                    source=source,
                    output_root=output_root,
                    index=len(files),
                    runtime=runtime,
                    spec_context=spec_context,
                    template_package=template_package,
                )
            )

    return tuple(files)