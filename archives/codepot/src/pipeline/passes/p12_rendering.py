"""Pass 12: template rendering."""

from __future__ import annotations

from dataclasses import replace

from archives.codepot.src.pipeline.contracts.diagnostics import PipelineDiagnostic, PipelineDiagnosticLevel
from archives.codepot.src.pipeline.contracts.results import ReportCounter
from archives.codepot.src.pipeline.contracts.state import PipelineState
from archives.codepot.src.pipeline.emission.renderer import render_template_contexts
from archives.codepot.src.pipeline.passes.base import (
    PassResult,
    failed_result,
    skipped_result,
    success_result,
    utc_now,
)


class RenderingPass:
    """Render planned template contexts into output file content."""

    name = "p12_rendering"
    title = "Render templates"

    def run(self, state: PipelineState) -> PassResult:
        """Render planned template contexts."""

        started_at = utc_now()

        if not state.options.render:
            return skipped_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Rendering skipped by options.",
                started_at=started_at,
            )

        if state.template_package is None:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Template rendering failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="template_package_missing",
                    message="Template package is required before rendering.",
                ),
            )

        if state.template_contexts is None:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Template rendering failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="template_contexts_missing",
                    message="Template contexts are required before rendering.",
                ),
            )

        try:
            rendered = render_template_contexts(
                package_path=state.template_package.package_path,
                contexts=state.template_contexts,
            )
        except ValueError as error:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Template rendering failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="template_rendering_failed",
                    message=str(error),
                ),
            )

        next_state = replace(state, rendered_files=rendered)

        return success_result(
            state=next_state,
            name=self.name,
            title=self.title,
            message="Templates rendered.",
            started_at=started_at,
            counters=(ReportCounter("files", len(rendered.files)),),
        )
