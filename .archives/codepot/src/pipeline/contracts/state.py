"""Pipeline state contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from archives.codepot.src.contracts.language.interface import LanguageAdapter
from archives.codepot.src.contracts.language.runtime import LanguageRuntime
from archives.codepot.src.contracts.spec.context import SpecContext
from archives.codepot.src.contracts.templates.config.package import LoadedTemplatePackageConfig
from archives.codepot.src.pipeline.contracts.options import PipelineOptions
from archives.codepot.src.pipeline.emission.graph import EmissionGraph
from archives.codepot.src.pipeline.emission.renderer import RenderedFiles
from archives.codepot.src.pipeline.emission.writer import FileWriteResults
from archives.codepot.src.pipeline.planning.contexts import PlannedTemplateContexts
from archives.codepot.src.pipeline.planning.dependencies import PlannedFileDependencies
from archives.codepot.src.pipeline.planning.files import PlannedOutputFile
from archives.codepot.src.pipeline.planning.imports import PlannedImportsExports
from archives.codepot.src.pipeline.planning.language import PlannedLanguageEnrichment
from archives.codepot.src.pipeline.planning.selections import PlannedSelection
from archives.codepot.src.spec.repository.repository import SpecRepository

if TYPE_CHECKING:
    from archives.codepot.src.pipeline.templates.validator import TemplateValidationResult


@dataclass(frozen=True)
class PipelineState:
    """Immutable state passed through all pipeline passes."""

    options: PipelineOptions

    spec_repository: SpecRepository | None = None
    spec_context: SpecContext | None = None

    template_package: LoadedTemplatePackageConfig | None = None
    template_validation: TemplateValidationResult | None = None

    language_adapter: LanguageAdapter | None = None
    language_runtime: LanguageRuntime | None = None

    # Later batches will replace these with typed planning/emission models.
    selections: tuple[PlannedSelection, ...] = ()
    output_files: tuple[PlannedOutputFile, ...] = ()
    file_dependencies: PlannedFileDependencies | None = None
    language_enrichment: PlannedLanguageEnrichment | None = None
    imports_exports: PlannedImportsExports | None = None
    template_contexts: PlannedTemplateContexts | None = None
    rendered_files: RenderedFiles | None = None
    write_results: FileWriteResults | None = None
    emission_graph: EmissionGraph | None = None
