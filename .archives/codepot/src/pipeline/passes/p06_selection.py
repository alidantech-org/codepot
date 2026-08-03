"""Pass 06: template selection planning."""

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
from archives.codepot.src.pipeline.planning.selections import (
    include_template,
    plan_template_selection,
)


class SelectionPlanningPass:
    """Plan selected spec records for template entries."""

    name = "p06_selection"
    title = "Plan selections"

    def run(self, state: PipelineState) -> PassResult:
        """Plan template selections."""

        started_at = utc_now()

        if state.spec_repository is None:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Template selection planning failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="spec_repository_missing",
                    message="Spec repository must be loaded before selection planning.",
                ),
            )

        if state.template_package is None:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Template selection planning failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="template_package_missing",
                    message="Template package must be loaded before selection planning.",
                ),
            )

        planned = tuple(
            plan_template_selection(
                template_id=template_id,
                template=template,
                repository=state.spec_repository,
            )
            for template_id, template in state.template_package.config.templates.items()
            if include_template(
                template_id=template_id,
                select=template.select,
                template_filters=state.options.template_ids,
                select_filters=state.options.select,
            )
        )

        selected_records_count = sum(len(selection.records) for selection in planned)
        selected_buckets_count = sum(len(selection.buckets) for selection in planned)

        next_state = replace(state, selections=planned)

        return success_result(
            state=next_state,
            name=self.name,
            title=self.title,
            message="Template selections planned.",
            started_at=started_at,
            counters=(
                ReportCounter("templates", len(planned)),
                ReportCounter("records", selected_records_count),
                ReportCounter("buckets", selected_buckets_count),
            ),
        )
