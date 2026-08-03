"""File-level import/export planning models and helpers."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.contracts.language.exports import LanguageExport, LanguageExportStrategy
from archives.codepot.src.contracts.language.imports import LanguageImport
from archives.codepot.src.contracts.language.interface import (
    LanguageAdapter,
    LanguageExportRequest,
    LanguageExportTarget,
    LanguageImportRequest,
    LanguageImportTarget,
)
from archives.codepot.src.contracts.language.runtime import LanguageRuntime
from archives.codepot.src.contracts.spec.records import SpecRecord
from archives.codepot.src.pipeline.planning.files import PlannedOutputFile


@dataclass(frozen=True)
class PlannedFileImportsExports:
    """Imports and exports planned for one output file."""

    file_id: str
    imports: tuple[LanguageImport, ...]
    exports: tuple[LanguageExport, ...]


@dataclass(frozen=True)
class PlannedImportsExports:
    """All file-level imports and exports."""

    files: tuple[PlannedFileImportsExports, ...]


@dataclass(frozen=True)
class RecordOutputIndex:
    """Index from spec record id to planned output file."""

    items: dict[str, PlannedOutputFile]

    def find_file_for_record(
        self,
        record: SpecRecord[object],
    ) -> PlannedOutputFile | None:
        """Find the planned file that emits a record."""

        return self.items.get(record.id)


@dataclass(frozen=True)
class FileOutputIndex:
    """Index from planned file id to planned output file."""

    items: dict[str, PlannedOutputFile]

    def find_file(
        self,
        file_id: str,
    ) -> PlannedOutputFile | None:
        """Find a planned file by id."""

        return self.items.get(file_id)


def build_record_output_index(
    files: tuple[PlannedOutputFile, ...],
) -> RecordOutputIndex:
    """Build record-to-file index from planned output files."""

    index: dict[str, PlannedOutputFile] = {}

    for file in files:
        if file.is_barrel or file.is_static or file.render_once:
            continue

        for record in file.source.records:
            index[record.id] = file

    return RecordOutputIndex(items=index)


def build_file_output_index(
    files: tuple[PlannedOutputFile, ...],
) -> FileOutputIndex:
    """Build planned-file id index."""

    return FileOutputIndex(items={file.id: file for file in files})


def _import_targets_for_file(
    *,
    file: PlannedOutputFile,
    index: RecordOutputIndex,
) -> tuple[LanguageImportTarget, ...]:
    """Build import targets for one planned file.

    Dependency target resolution requires typed dependency target ids. Until
    SpecDependency exposes resolved target ids, imports are intentionally empty.
    """

    return ()


def _symbol_for_record(record: SpecRecord[object]) -> str:
    """Return a stable exported symbol for a record.

    This is intentionally based on typed SpecName data, not guessed object shape.
    Language-specific enrichment can replace this later.
    """

    return record.name.pascal


def _barrel_star_export_targets(
    *,
    file: PlannedOutputFile,
    file_index: FileOutputIndex,
) -> tuple[LanguageExportTarget, ...]:
    """Build star export targets for one barrel file."""

    targets: list[LanguageExportTarget] = []

    for source_file_id in file.barrel_source_file_ids:
        source_file = file_index.find_file(source_file_id)

        if source_file is None:
            raise ValueError(f"Barrel source file was not found: {source_file_id}")

        targets.append(
            LanguageExportTarget(
                symbol="*",
                target_path=source_file.output_path,
                source_path=file.output_path,
            )
        )

    return tuple(targets)


def _barrel_named_export_targets(
    *,
    file: PlannedOutputFile,
    file_index: FileOutputIndex,
) -> tuple[LanguageExportTarget, ...]:
    """Build named export targets for one barrel file."""

    targets: list[LanguageExportTarget] = []

    for source_file_id in file.barrel_source_file_ids:
        source_file = file_index.find_file(source_file_id)

        if source_file is None:
            raise ValueError(f"Barrel source file was not found: {source_file_id}")

        for record in source_file.source.records:
            targets.append(
                LanguageExportTarget(
                    symbol=_symbol_for_record(record),
                    target_path=source_file.output_path,
                    source_path=file.output_path,
                )
            )

    return tuple(targets)


def _export_targets_for_file(
    *,
    file: PlannedOutputFile,
    file_index: FileOutputIndex,
) -> tuple[LanguageExportTarget, ...]:
    """Build export targets for one file."""

    if not file.is_barrel:
        return ()

    strategy = _export_strategy_for_file(file)

    if strategy == LanguageExportStrategy.STAR:
        return _barrel_star_export_targets(
            file=file,
            file_index=file_index,
        )

    return _barrel_named_export_targets(
        file=file,
        file_index=file_index,
    )


def _export_strategy_for_file(file: PlannedOutputFile) -> LanguageExportStrategy:
    """Resolve export strategy for one file."""

    if not file.is_barrel:
        return LanguageExportStrategy.NAMED

    return LanguageExportStrategy(file.template.barrel_export)


def plan_file_imports_exports(
    *,
    file: PlannedOutputFile,
    record_index: RecordOutputIndex,
    file_index: FileOutputIndex,
    adapter: LanguageAdapter,
    runtime: LanguageRuntime,
) -> PlannedFileImportsExports:
    """Plan imports/exports for one planned output file."""

    import_targets = _import_targets_for_file(file=file, index=record_index)
    export_targets = _export_targets_for_file(file=file, file_index=file_index)

    imports = adapter.create_imports(
        LanguageImportRequest(
            source_path=file.output_path,
            targets=import_targets,
            runtime=runtime,
        )
    )

    exports = adapter.create_exports(
        LanguageExportRequest(
            source_path=file.output_path,
            targets=export_targets,
            strategy=_export_strategy_for_file(file),
            runtime=runtime,
        )
    )

    return PlannedFileImportsExports(
        file_id=file.id,
        imports=imports,
        exports=exports,
    )


def plan_imports_exports(
    *,
    files: tuple[PlannedOutputFile, ...],
    adapter: LanguageAdapter,
    runtime: LanguageRuntime,
) -> PlannedImportsExports:
    """Plan file-level imports and exports for all files."""

    record_index = build_record_output_index(files)
    file_index = build_file_output_index(files)

    return PlannedImportsExports(
        files=tuple(
            plan_file_imports_exports(
                file=file,
                record_index=record_index,
                file_index=file_index,
                adapter=adapter,
                runtime=runtime,
            )
            for file in files
        )
    )