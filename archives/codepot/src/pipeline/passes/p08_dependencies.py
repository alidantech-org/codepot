"""Pass 08: dependency planning."""

from __future__ import annotations

from dataclasses import replace

from archives.codepot.src.pipeline.contracts.results import ReportCounter
from archives.codepot.src.pipeline.contracts.state import PipelineState
from archives.codepot.src.pipeline.passes.base import PassResult, success_result, utc_now
from archives.codepot.src.pipeline.planning.dependencies import plan_file_dependencies


class DependencyPlanningPass:
    """Plan dependencies for planned output files."""

    name = "p08_dependencies"
    title = "Plan dependencies"

    def run(self, state: PipelineState) -> PassResult:
        """Plan file dependencies."""

        started_at = utc_now()

        planned = plan_file_dependencies(state.output_files)
        next_state = replace(state, file_dependencies=planned)

        return success_result(
            state=next_state,
            name=self.name,
            title=self.title,
            message="File dependencies planned.",
            started_at=started_at,
            counters=(ReportCounter("dependencies", len(planned.items)),),
        )
