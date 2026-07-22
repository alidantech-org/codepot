"""Pass 13: rendered file writing."""

from __future__ import annotations

from dataclasses import replace

from archives.codepot.src.pipeline.contracts.diagnostics import PipelineDiagnostic, PipelineDiagnosticLevel
from archives.codepot.src.pipeline.contracts.results import ReportCounter
from archives.codepot.src.pipeline.contracts.state import PipelineState
from archives.codepot.src.pipeline.emission.writer import write_rendered_files
from archives.codepot.src.pipeline.passes.base import (
    PassResult,
    failed_result,
    skipped_result,
    success_result,
    utc_now,
)


class WritingPass:
    """Write rendered files to disk, or report dry-run changes."""

    name = "p13_writing"
    title = "Write files"

    def run(self, state: PipelineState) -> PassResult:
        """Write rendered files."""

        started_at = utc_now()

        if not state.options.write:
            return skipped_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Writing skipped by options.",
                started_at=started_at,
            )

        if state.rendered_files is None:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="File writing failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="rendered_files_missing",
                    message="Rendered files are required before writing.",
                ),
            )

        try:
            results = write_rendered_files(
                rendered=state.rendered_files,
                dry_run=state.options.dry_run,
            )
        except ValueError as error:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="File writing failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="file_writing_failed",
                    message=str(error),
                ),
            )

        next_state = replace(state, write_results=results)

        if state.options.dry_run:
            message = "Dry-run write plan completed."
        else:
            message = "Rendered files written."

        return success_result(
            state=next_state,
            name=self.name,
            title=self.title,
            message=message,
            started_at=started_at,
            counters=(
                ReportCounter("files", len(results.files)),
                ReportCounter("created", results.created),
                ReportCounter("updated", results.updated),
                ReportCounter("unchanged", results.unchanged),
                ReportCounter("would_create", results.would_create),
                ReportCounter("would_update", results.would_update),
                ReportCounter("skipped", results.skipped),
            ),
        )
