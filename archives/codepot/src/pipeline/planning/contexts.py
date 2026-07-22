"""Final template context planning models and helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from archives.codepot.src.contracts.language.context import LanguageItem
from archives.codepot.src.contracts.language.exports import LanguageExport
from archives.codepot.src.contracts.language.imports import LanguageImport
from archives.codepot.src.contracts.language.runtime import LanguageRuntime
from archives.codepot.src.contracts.spec.context import SpecContext
from archives.codepot.src.contracts.spec.records import SpecRecord
from archives.codepot.src.contracts.templates.config.template import TemplateEntryConfig
from archives.codepot.src.pipeline.planning.files import PlannedOutputFile
from archives.codepot.src.pipeline.planning.imports import PlannedImportsExports
from archives.codepot.src.pipeline.planning.language import PlannedLanguageEnrichment


@dataclass(frozen=True)
class TemplateRecordContext:
    """Template-facing record context."""

    record: SpecRecord[object]
    lang: LanguageItem | None = None


@dataclass(frozen=True)
class TemplateFileContext:
    """Final context for one file render/write."""

    file_id: str
    template_id: str
    template: TemplateEntryConfig

    output_path: Path
    relative_output_path: str

    language: LanguageRuntime
    spec: SpecContext

    records: tuple[TemplateRecordContext, ...]
    imports: tuple[LanguageImport, ...]
    exports: tuple[LanguageExport, ...]

    template_file: str | None = None
    source_template_path: Path | None = None
    is_static: bool = False
    render_once: bool = False


@dataclass(frozen=True)
class PlannedTemplateContexts:
    """All planned template render/write contexts."""

    files: tuple[TemplateFileContext, ...]


def _language_items_for_file(
    *,
    file: PlannedOutputFile,
    enrichment: PlannedLanguageEnrichment | None,
) -> dict[str, LanguageItem]:
    """Return language item map for one planned file."""

    if enrichment is None:
        return {}

    for enriched_file in enrichment.files:
        if enriched_file.file_id == file.id:
            return {item.record.id: item.lang for item in enriched_file.items}

    return {}


def _imports_exports_for_file(
    *,
    file: PlannedOutputFile,
    imports_exports: PlannedImportsExports | None,
) -> tuple[tuple[LanguageImport, ...], tuple[LanguageExport, ...]]:
    """Return imports and exports for one planned file."""

    if imports_exports is None:
        return (), ()

    for planned_file in imports_exports.files:
        if planned_file.file_id == file.id:
            return planned_file.imports, planned_file.exports

    return (), ()


def _record_contexts(
    *,
    file: PlannedOutputFile,
    enrichment: PlannedLanguageEnrichment | None,
) -> tuple[TemplateRecordContext, ...]:
    """Build record contexts for one file."""

    language_items = _language_items_for_file(
        file=file,
        enrichment=enrichment,
    )

    return tuple(
        TemplateRecordContext(
            record=record,
            lang=language_items.get(record.id),
        )
        for record in file.source.records
    )


def build_template_file_context(
    *,
    file: PlannedOutputFile,
    language: LanguageRuntime,
    spec: SpecContext,
    enrichment: PlannedLanguageEnrichment | None,
    imports_exports: PlannedImportsExports | None,
) -> TemplateFileContext:
    """Build final template context for one planned file."""

    imports, exports = _imports_exports_for_file(
        file=file,
        imports_exports=imports_exports,
    )

    return TemplateFileContext(
        file_id=file.id,
        template_id=file.template_id,
        template=file.template,
        template_file=file.template_file,
        source_template_path=file.source_template_path,
        output_path=file.output_path,
        relative_output_path=file.relative_output_path,
        language=language,
        spec=spec,
        records=_record_contexts(file=file, enrichment=enrichment),
        imports=imports,
        exports=exports,
        is_static=file.is_static,
        render_once=file.render_once,
    )


def build_template_contexts(
    *,
    files: tuple[PlannedOutputFile, ...],
    language: LanguageRuntime,
    spec: SpecContext,
    enrichment: PlannedLanguageEnrichment | None,
    imports_exports: PlannedImportsExports | None,
) -> PlannedTemplateContexts:
    """Build final template contexts for all planned files."""

    return PlannedTemplateContexts(
        files=tuple(
            build_template_file_context(
                file=file,
                language=language,
                spec=spec,
                enrichment=enrichment,
                imports_exports=imports_exports,
            )
            for file in files
        )
    )