"""Pipeline pass registry."""

from __future__ import annotations

from archives.codepot.src.pipeline.passes.base import PipelinePass
from archives.codepot.src.pipeline.passes.p01_inputs import InputResolutionPass
from archives.codepot.src.pipeline.passes.p02_spec_repository import SpecRepositoryPass
from archives.codepot.src.pipeline.passes.p03_template_package import TemplatePackagePass
from archives.codepot.src.pipeline.passes.p04_template_validation import TemplateValidationPass
from archives.codepot.src.pipeline.passes.p05_language_runtime import LanguageRuntimePass
from archives.codepot.src.pipeline.passes.p06_selection import SelectionPlanningPass
from archives.codepot.src.pipeline.passes.p07_output_plan import OutputPlanningPass
from archives.codepot.src.pipeline.passes.p08_dependencies import DependencyPlanningPass
from archives.codepot.src.pipeline.passes.p09_language_enrichment import LanguageEnrichmentPass
from archives.codepot.src.pipeline.passes.p10_imports_exports import ImportsExportsPass
from archives.codepot.src.pipeline.passes.p11_template_context import TemplateContextPass
from archives.codepot.src.pipeline.passes.p12_rendering import RenderingPass
from archives.codepot.src.pipeline.passes.p13_writing import WritingPass
from archives.codepot.src.pipeline.passes.p14_emission_graph import EmissionGraphPass


def create_default_passes() -> tuple[PipelinePass, ...]:
    """Create the default ordered pipeline pass list."""

    return (
        InputResolutionPass(),
        SpecRepositoryPass(),
        TemplatePackagePass(),
        TemplateValidationPass(),
        LanguageRuntimePass(),
        SelectionPlanningPass(),
        OutputPlanningPass(),
        DependencyPlanningPass(),
        LanguageEnrichmentPass(),
        ImportsExportsPass(),
        TemplateContextPass(),
        RenderingPass(),
        WritingPass(),
        EmissionGraphPass(),
    )
