"""Language enrichment planning models and helpers."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.contracts.language.context import LanguageItem
from archives.codepot.src.contracts.language.interface import LanguageAdapter, LanguageItemRequest
from archives.codepot.src.contracts.language.runtime import LanguageRuntime
from archives.codepot.src.contracts.spec.records import SpecRecord
from archives.codepot.src.pipeline.planning.files import PlannedOutputFile


@dataclass(frozen=True)
class PlannedLanguageItem:
    """Language enrichment for one spec record."""

    record: SpecRecord[object]
    lang: LanguageItem


@dataclass(frozen=True)
class PlannedLanguageFile:
    """Language enrichment attached to one planned output file."""

    file_id: str
    items: tuple[PlannedLanguageItem, ...]


@dataclass(frozen=True)
class PlannedLanguageEnrichment:
    """All language enrichment produced for planned files."""

    files: tuple[PlannedLanguageFile, ...]


def enrich_record(
    *,
    record: SpecRecord[object],
    adapter: LanguageAdapter,
    runtime: LanguageRuntime,
) -> PlannedLanguageItem:
    """Enrich one spec record with language metadata."""

    lang = adapter.enrich_item(
        LanguageItemRequest(
            record=record,
            runtime=runtime,
        )
    )

    return PlannedLanguageItem(
        record=record,
        lang=lang,
    )


def enrich_file(
    *,
    file: PlannedOutputFile,
    adapter: LanguageAdapter,
    runtime: LanguageRuntime,
) -> PlannedLanguageFile:
    """Enrich records included in one planned output file."""

    items = tuple(
        enrich_record(
            record=record,
            adapter=adapter,
            runtime=runtime,
        )
        for record in file.source.records
    )

    return PlannedLanguageFile(
        file_id=file.id,
        items=items,
    )


def plan_language_enrichment(
    *,
    files: tuple[PlannedOutputFile, ...],
    adapter: LanguageAdapter,
    runtime: LanguageRuntime,
) -> PlannedLanguageEnrichment:
    """Enrich planned output files with language metadata."""

    return PlannedLanguageEnrichment(
        files=tuple(
            enrich_file(
                file=file,
                adapter=adapter,
                runtime=runtime,
            )
            for file in files
        )
    )
