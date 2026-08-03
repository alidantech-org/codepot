"""Pass 03: template package loading."""

from __future__ import annotations

from dataclasses import replace

from archives.codepot.src.pipeline.contracts.diagnostics import (
    PipelineDiagnostic,
    PipelineDiagnosticLevel,
)
from archives.codepot.src.pipeline.contracts.results import ReportCounter
from archives.codepot.src.pipeline.contracts.state import PipelineState
from archives.codepot.src.pipeline.passes.base import (
    PassResult,
    failed_result,
    success_result,
    utc_now,
)
from archives.codepot.src.pipeline.templates.loader import load_template_package


class TemplatePackagePass:
    """Load and parse template package config."""

    name = "p03_template_package"
    title = "Load template package"

    def run(self, state: PipelineState) -> PassResult:
        """Load template package config."""

        started_at = utc_now()

        try:
            loaded = load_template_package(state.options.template_package_path)
        except (FileNotFoundError, ValueError) as error:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Template package loading failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="template_package_load_failed",
                    message=str(error),
                ),
            )

        next_state = replace(state, template_package=loaded)

        return success_result(
            state=next_state,
            name=self.name,
            title=self.title,
            message="Template package loaded.",
            started_at=started_at,
            counters=(
                ReportCounter("templates", len(loaded.config.templates)),
                ReportCounter("format", 1, loaded.format.value),
            ),
        )
