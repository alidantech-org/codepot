"""Pass 14: emission graph building."""

from __future__ import annotations

from dataclasses import replace

from archives.codepot.src.pipeline.contracts.diagnostics import (
    PipelineDiagnostic,
    PipelineDiagnosticLevel,
)
from archives.codepot.src.pipeline.contracts.results import (
    PassStatus,
    PipelineReport,
    ReportCounter,
)
from archives.codepot.src.pipeline.contracts.state import PipelineState
from archives.codepot.src.pipeline.emission.artifacts import write_emission_graph
from archives.codepot.src.pipeline.emission.graph import build_emission_graph
from archives.codepot.src.pipeline.passes.base import (
    PassResult,
    failed_result,
    skipped_result,
    success_result,
    utc_now,
)


class EmissionGraphPass:
    """Build and optionally write final emission graph artifact."""

    name = "p14_emission_graph"
    title = "Build emission graph"

    def run(self, state: PipelineState) -> PassResult:
        """Build emission graph."""

        started_at = utc_now()

        if not state.options.write_graph:
            return skipped_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Emission graph skipped by options.",
                started_at=started_at,
            )

        if state.template_contexts is None:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Emission graph building failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="template_contexts_missing",
                    message="Template contexts are required before graph building.",
                ),
            )

        placeholder_report = PipelineReport(
            status=PassStatus.SUCCESS,
            reports=(),
            diagnostics=(),
        )

        try:
            graph = build_emission_graph(
                output_root=state.options.output_path,
                contexts=state.template_contexts,
                files=state.output_files,
                write_results=state.write_results,
                report=placeholder_report,
            )
            written_path = write_emission_graph(
                output_root=state.options.output_path,
                graph=graph,
                dry_run=state.options.dry_run,
            )
        except ValueError as error:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Emission graph building failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="emission_graph_failed",
                    message=str(error),
                ),
            )

        next_state = replace(state, emission_graph=graph)

        message = (
            f"Emission graph planned: {written_path}"
            if state.options.dry_run
            else f"Emission graph written: {written_path}"
        )

        return success_result(
            state=next_state,
            name=self.name,
            title=self.title,
            message=message,
            started_at=started_at,
            counters=(
                ReportCounter("templates", len(graph.templates)),
                ReportCounter("files", len(graph.files)),
                ReportCounter("artifacts", 1),
            ),
        )
