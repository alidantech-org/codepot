"""Pass 05: language runtime resolution."""

from __future__ import annotations

from dataclasses import replace

from archives.codepot.src.contracts.language.interface import LanguageRuntimeRequest
from archives.codepot.src.languages.registry import language_registry
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


class LanguageRuntimePass:
    """Resolve language adapter and runtime."""

    name = "p05_language_runtime"
    title = "Resolve language runtime"

    def run(self, state: PipelineState) -> PassResult:
        """Resolve selected language adapter and runtime."""

        started_at = utc_now()

        if state.template_package is None:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Language runtime resolution failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="template_package_missing",
                    message="Template package must be loaded before language runtime.",
                ),
            )

        config = state.template_package.config
        language_key = state.options.language or config.language.name

        try:
            adapter = language_registry.get(language_key)
        except ValueError as error:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Language adapter was not found.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="language_adapter_missing",
                    message=str(error),
                ),
            )

        runtime = adapter.create_runtime(
            LanguageRuntimeRequest(
                language=language_key,
                extensions=config.language.extensions,
                package_name=config.language.package_name,
                package_manager=config.language.package_manager,
                source_root=state.template_package.package_path
                / config.language.source_root,
                naming=config.language.naming,
                imports=config.language.imports,
            )
        )

        next_state = replace(
            state,
            language_adapter=adapter,
            language_runtime=runtime,
        )

        return success_result(
            state=next_state,
            name=self.name,
            title=self.title,
            message=f"Language runtime resolved: {language_key}.",
            started_at=started_at,
            counters=(
                ReportCounter("language", 1, language_key),
                ReportCounter("extensions", len(runtime.extensions), ",".join(runtime.extensions)),
            ),
        )