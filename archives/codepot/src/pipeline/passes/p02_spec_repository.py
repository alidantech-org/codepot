"""Pass 02: spec repository loading."""

from __future__ import annotations

from dataclasses import replace

from archives.codepot.src.pipeline.contracts.results import ReportCounter
from archives.codepot.src.pipeline.contracts.state import PipelineState
from archives.codepot.src.pipeline.passes.base import PassResult, success_result, utc_now
from archives.codepot.src.spec.repository import SpecRepository


class SpecRepositoryPass:
    """Load the compiled spec into the typed repository."""

    name = "p02_spec_repository"
    title = "Load spec repository"

    def run(self, state: PipelineState) -> PassResult:
        """Load spec repository and context."""

        started_at = utc_now()

        repository = SpecRepository.from_file(state.options.spec_path)
        context = repository.get_context()
        counts = repository.get_counts()

        next_state = replace(
            state,
            spec_repository=repository,
            spec_context=context,
        )

        return success_result(
            state=next_state,
            name=self.name,
            title=self.title,
            message="Spec repository loaded.",
            started_at=started_at,
            counters=(
                ReportCounter("records", counts.records_total),
                ReportCounter("resources", counts.resources),
                ReportCounter("models", counts.models),
                ReportCounter("dtos", counts.dtos),
                ReportCounter("routes", counts.routes),
            ),
        )
