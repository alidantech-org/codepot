"""Pipeline runner.

This is the only root pipeline module. It orchestrates registered passes and
returns the final state/report.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from archives.codepot.src.pipeline.contracts.diagnostics import PipelineDiagnostic
from archives.codepot.src.pipeline.contracts.events import PipelineEvent, PipelineEventLevel
from archives.codepot.src.pipeline.contracts.options import PipelineOptions
from archives.codepot.src.pipeline.contracts.results import PassReport, PassStatus, PipelineReport
from archives.codepot.src.pipeline.contracts.state import PipelineState
from archives.codepot.src.pipeline.debug.state_dump import (
    PipelineStateDumpRequest,
    write_pipeline_state_dump,
)
from archives.codepot.src.pipeline.passes.base import PipelinePass
from archives.codepot.src.pipeline.passes.registry import create_default_passes

PipelineReporter = Callable[[PipelineEvent], None]

@dataclass(frozen=True)
class PipelineRunResult:
    """Final pipeline execution result."""

    state: PipelineState
    report: PipelineReport


def _event(pass_name: str, message: str) -> PipelineEvent:
    """Create a pipeline info event."""

    return PipelineEvent(
        level=PipelineEventLevel.INFO,
        pass_name=pass_name,
        message=message,
        timestamp=datetime.now(UTC),
    )


def _status_from_reports(reports: tuple[PassReport, ...]) -> PassStatus:
    """Compute final pipeline status from pass reports."""

    if any(report.status == PassStatus.FAILED for report in reports):
        return PassStatus.FAILED

    if any(report.status == PassStatus.WARNING for report in reports):
        return PassStatus.WARNING

    return PassStatus.SUCCESS


def _diagnostics_from_reports(
    reports: tuple[PassReport, ...],
) -> tuple[PipelineDiagnostic, ...]:
    """Collect diagnostics from pass reports."""

    return tuple(diagnostic for report in reports for diagnostic in report.diagnostics)


@dataclass(frozen=True)
class Pipeline:
    """Pass-based emission pipeline."""

    passes: tuple[PipelinePass, ...]

    @classmethod
    def create_default(cls) -> "Pipeline":  # noqa: UP037
        """Create the default pipeline."""

        return cls(passes=create_default_passes())

    def run(
        self, options: PipelineOptions, reporter: PipelineReporter | None = None
    ) -> PipelineRunResult:
        """Run all configured passes."""

        state = PipelineState(options=options)
        reports: list[PassReport] = []

        for index, pipeline_pass in enumerate(self.passes, start=1):
            if reporter is not None:
                reporter(_event(pipeline_pass.name, f"Starting {pipeline_pass.title}"))

            result = pipeline_pass.run(state)
            state = result.state
            reports.append(result.report)

            if state.options.debug:
                write_pipeline_state_dump(
                    PipelineStateDumpRequest(
                        index=index,
                        state=state,
                        report=result.report,
                    )
                )

            if reporter is not None:
                reporter(_event(pipeline_pass.name, result.report.message))

            if result.report.status == PassStatus.FAILED:
                break

        final_reports = tuple(reports)
        report = PipelineReport(
            status=_status_from_reports(final_reports),
            reports=final_reports,
            diagnostics=_diagnostics_from_reports(final_reports),
        )

        return PipelineRunResult(state=state, report=report)
