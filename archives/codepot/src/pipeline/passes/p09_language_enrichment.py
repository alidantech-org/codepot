"""Pass 09: language enrichment."""

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
from archives.codepot.src.pipeline.planning.language import plan_language_enrichment


class LanguageEnrichmentPass:
    """Enrich selected records with language-specific metadata."""

    name = "p09_language_enrichment"
    title = "Enrich language context"

    def run(self, state: PipelineState) -> PassResult:
        """Run language enrichment."""

        started_at = utc_now()

        if state.language_adapter is None:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Language enrichment failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="language_adapter_missing",
                    message="Language adapter must be resolved before enrichment.",
                ),
            )

        if state.language_runtime is None:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Language enrichment failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="language_runtime_missing",
                    message="Language runtime must be resolved before enrichment.",
                ),
            )

        enrichment = plan_language_enrichment(
            files=state.output_files,
            adapter=state.language_adapter,
            runtime=state.language_runtime,
        )

        next_state = replace(
            state,
            language_enrichment=enrichment,
        )

        files_count = len(enrichment.files)
        items_count = sum(len(file.items) for file in enrichment.files)

        return success_result(
            state=next_state,
            name=self.name,
            title=self.title,
            message="Language context enriched.",
            started_at=started_at,
            counters=(
                ReportCounter("files", files_count),
                ReportCounter("items", items_count),
            ),
        )
