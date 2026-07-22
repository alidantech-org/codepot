"""Pass 01: input resolution."""

from __future__ import annotations

from archives.codepot.src.pipeline.contracts.diagnostics import PipelineDiagnostic, PipelineDiagnosticLevel
from archives.codepot.src.pipeline.contracts.results import PassStatus
from archives.codepot.src.pipeline.contracts.state import PipelineState
from archives.codepot.src.pipeline.passes.base import PassResult, make_report, utc_now


class InputResolutionPass:
    """Validate and resolve input paths/options."""

    name = "p01_inputs"
    title = "Resolve inputs"

    def run(self, state: PipelineState) -> PassResult:
        """Validate required input paths."""

        started_at = utc_now()
        diagnostics: list[PipelineDiagnostic] = []

        options = state.options

        if not options.spec_path.is_file():
            diagnostics.append(
                PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="spec_file_missing",
                    message=f"Spec file does not exist: {options.spec_path}",
                )
            )

        if not options.template_package_path.exists():
            diagnostics.append(
                PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="template_package_missing",
                    message=(
                        "Template package path does not exist: "
                        f"{options.template_package_path}"
                    ),
                )
            )

        status = PassStatus.FAILED if diagnostics else PassStatus.SUCCESS
        message = "Input validation failed." if diagnostics else "Inputs resolved."

        report = make_report(
            name=self.name,
            title=self.title,
            status=status,
            message=message,
            started_at=started_at,
            diagnostics=tuple(diagnostics),
        )

        return PassResult(state=state, report=report)
