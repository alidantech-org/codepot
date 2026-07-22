"""Pass 04: template package validation."""

from __future__ import annotations

from dataclasses import replace

from archives.codepot.src.pipeline.contracts.diagnostics import PipelineDiagnostic, PipelineDiagnosticLevel
from archives.codepot.src.pipeline.contracts.results import PassStatus, ReportCounter
from archives.codepot.src.pipeline.contracts.state import PipelineState
from archives.codepot.src.pipeline.passes.base import PassResult, failed_result, make_report, utc_now
from archives.codepot.src.pipeline.templates.validator import validate_template_package


class TemplateValidationPass:
    """Validate loaded template package config."""

    name = "p04_template_validation"
    title = "Validate template package"

    def run(self, state: PipelineState) -> PassResult:
        """Validate template package."""

        started_at = utc_now()

        if state.template_package is None:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Template validation failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="template_package_missing",
                    message="Template package must be loaded before validation.",
                ),
            )

        validation = validate_template_package(state.template_package)
        next_state = replace(state, template_validation=validation)

        diagnostics = tuple(
            PipelineDiagnostic(
                level=PipelineDiagnosticLevel.ERROR,
                pass_name=self.name,
                code="template_validation_error",
                message=error.message,
                detail=error.template_id,
            )
            for error in validation.errors
        ) + tuple(
            PipelineDiagnostic(
                level=PipelineDiagnosticLevel.WARNING,
                pass_name=self.name,
                code="template_validation_warning",
                message=warning.message,
                detail=warning.template_id,
            )
            for warning in validation.warnings
        )

        status = PassStatus.SUCCESS
        message = "Template package is valid."

        if validation.errors:
            status = PassStatus.FAILED
            message = "Template package validation failed."
        elif validation.warnings:
            status = PassStatus.WARNING
            message = "Template package validated with warnings."

        report = make_report(
            name=self.name,
            title=self.title,
            status=status,
            message=message,
            started_at=started_at,
            counters=(
                ReportCounter("errors", len(validation.errors)),
                ReportCounter("warnings", len(validation.warnings)),
            ),
            diagnostics=diagnostics,
        )

        return PassResult(state=next_state, report=report)
