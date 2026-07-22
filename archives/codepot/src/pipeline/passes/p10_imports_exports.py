"""Pass 10: import/export planning."""

from __future__ import annotations

from dataclasses import replace

from archives.codepot.src.pipeline.contracts.diagnostics import PipelineDiagnostic, PipelineDiagnosticLevel
from archives.codepot.src.pipeline.contracts.results import ReportCounter
from archives.codepot.src.pipeline.contracts.state import PipelineState
from archives.codepot.src.pipeline.passes.base import (
    PassResult,
    failed_result,
    success_result,
    utc_now,
)
from archives.codepot.src.pipeline.planning.imports import plan_imports_exports


class ImportsExportsPass:
    """Plan file-level imports and exports."""

    name = "p10_imports_exports"
    title = "Plan imports and exports"

    def run(self, state: PipelineState) -> PassResult:
        """Plan imports and exports."""

        started_at = utc_now()

        if state.language_adapter is None:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Import/export planning failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="language_adapter_missing",
                    message="Language adapter must be resolved before import planning.",
                ),
            )

        if state.language_runtime is None:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Import/export planning failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="language_runtime_missing",
                    message="Language runtime must be resolved before import planning.",
                ),
            )

        planned = plan_imports_exports(
            files=state.output_files,
            adapter=state.language_adapter,
            runtime=state.language_runtime,
        )

        imports_count = sum(len(file.imports) for file in planned.files)
        exports_count = sum(len(file.exports) for file in planned.files)

        next_state = replace(state, imports_exports=planned)

        return success_result(
            state=next_state,
            name=self.name,
            title=self.title,
            message="Imports and exports planned.",
            started_at=started_at,
            counters=(
                ReportCounter("files", len(planned.files)),
                ReportCounter("imports", imports_count),
                ReportCounter("exports", exports_count),
            ),
        )
