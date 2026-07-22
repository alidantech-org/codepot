"""Pass 11: final template context planning."""

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
from archives.codepot.src.pipeline.planning.contexts import build_template_contexts


class TemplateContextPass:
    """Build final template render contexts."""

    name = "p11_template_context"
    title = "Build template contexts"

    def run(self, state: PipelineState) -> PassResult:
        """Build final template contexts."""

        started_at = utc_now()

        if state.language_runtime is None:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Template context planning failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="language_runtime_missing",
                    message="Language runtime is required before template context planning.",
                ),
            )

        if state.spec_context is None:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Template context planning failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="spec_context_missing",
                    message="Spec context is required before template context planning.",
                ),
            )

        contexts = build_template_contexts(
            files=state.output_files,
            language=state.language_runtime,
            spec=state.spec_context,
            enrichment=state.language_enrichment,
            imports_exports=state.imports_exports,
        )

        next_state = replace(state, template_contexts=contexts)

        records_count = sum(len(file.records) for file in contexts.files)
        imports_count = sum(len(file.imports) for file in contexts.files)
        exports_count = sum(len(file.exports) for file in contexts.files)

        return success_result(
            state=next_state,
            name=self.name,
            title=self.title,
            message="Template contexts built.",
            started_at=started_at,
            counters=(
                ReportCounter("files", len(contexts.files)),
                ReportCounter("records", records_count),
                ReportCounter("imports", imports_count),
                ReportCounter("exports", exports_count),
            ),
        )
