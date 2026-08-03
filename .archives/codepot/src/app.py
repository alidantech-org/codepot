"""Public Codepotx application API.

This module is intentionally thin. It exposes the main Codepotx facade used by
the CLI and future integrations, while relying on existing repository,
template, and pipeline contracts.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from archives.codepot.src.contracts.spec.context import SpecContext, SpecCounts, SpecMetadata
from archives.codepot.src.contracts.templates.config.package import LoadedTemplatePackageConfig
from archives.codepot.src.pipeline.contracts.options import PipelineOptions
from archives.codepot.src.pipeline.pipeline import Pipeline, PipelineReporter, PipelineRunResult
from archives.codepot.src.pipeline.templates.loader import load_template_package
from archives.codepot.src.pipeline.templates.validator import (
    TemplateValidationResult,
    validate_template_package,
)
from archives.codepot.src.spec.repository import SpecRepository


class Codepotx:
    """Public app facade for Codepotx features."""

    def __init__(self, pipeline: Pipeline | None = None) -> None:
        """Create app facade."""

        self._pipeline = pipeline or Pipeline.create_default()

    def repository(self, spec_path: Path) -> SpecRepository:
        """Load a typed spec repository."""

        return SpecRepository.from_file(spec_path)

    def context(self, spec_path: Path) -> SpecContext:
        """Load normalized spec context."""

        return self.repository(spec_path).get_context()

    def counts(self, spec_path: Path) -> SpecCounts:
        """Load normalized spec counts."""

        return self.repository(spec_path).get_counts()

    def metadata(self, spec_path: Path) -> SpecMetadata:
        """Load normalized spec metadata."""

        return self.repository(spec_path).get_metadata()

    def validate(self, spec_path: Path) -> SpecContext:
        """Validate a spec by loading its typed repository context."""

        return self.context(spec_path)

    def inspect(self, spec_path: Path) -> SpecContext:
        """Inspect a spec by returning its normalized context."""

        return self.context(spec_path)

    def load_template_package(self, template_package_path: Path) -> LoadedTemplatePackageConfig:
        """Load a typed template package config."""

        return load_template_package(template_package_path)

    def validate_template_package(
        self,
        template_package_path: Path,
    ) -> TemplateValidationResult:
        """Validate a template package."""

        package = self.load_template_package(template_package_path)
        return validate_template_package(package)

    def plan(
        self,
        options: PipelineOptions,
        reporter: PipelineReporter | None = None,
    ) -> PipelineRunResult:
        """Run the pipeline in planning mode."""

        plan_options = replace(
            options,
            dry_run=True,
            render=False,
            write=False,
            write_graph=False,
        )
        return self._pipeline.run(plan_options, reporter=reporter)

    def emit(
        self,
        options: PipelineOptions,
        reporter: PipelineReporter | None = None,
    ) -> PipelineRunResult:
        """Run the full emission pipeline."""

        return self._pipeline.run(options, reporter=reporter)

    def template_vars(self) -> None:
        """Return available template variables.

        This will be implemented after the template variable registry is built.
        """

        raise NotImplementedError("Template variable listing is not implemented yet.")

    def template_selections(self) -> None:
        """Return available template selections.

        This will be implemented after the selection registry is finalized.
        """

        raise NotImplementedError("Template selection listing is not implemented yet.")


codepotx = Codepotx()