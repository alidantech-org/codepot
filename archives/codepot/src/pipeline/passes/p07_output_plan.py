"""Pass 07: output file planning."""

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
from archives.codepot.src.pipeline.planning.outputs import plan_output_files


class OutputPlanningPass:
    """Plan output files from template package filesystem and selections."""

    name = "p07_output_plan"
    title = "Plan output files"

    def run(self, state: PipelineState) -> PassResult:
        """Plan output files."""

        started_at = utc_now()

        if state.language_runtime is None:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Output file planning failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="language_runtime_missing",
                    message="Language runtime must be resolved before output planning.",
                ),
            )

        if state.spec_context is None:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Output file planning failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="spec_context_missing",
                    message="Spec context must be loaded before output planning.",
                ),
            )

        if state.template_package is None:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Output file planning failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="template_package_missing",
                    message="Template package must be loaded before output planning.",
                ),
            )

        try:
            files = plan_output_files(
                selections=state.selections,
                output_root=state.options.output_path,
                runtime=state.language_runtime,
                spec_context=state.spec_context,
                template_package=state.template_package,
            )
        except ValueError as error:
            return failed_result(
                state=state,
                name=self.name,
                title=self.title,
                message="Output file planning failed.",
                started_at=started_at,
                diagnostic=PipelineDiagnostic(
                    level=PipelineDiagnosticLevel.ERROR,
                    pass_name=self.name,
                    code="output_path_planning_failed",
                    message=str(error),
                ),
            )

        debug = ()
        if state.options.debug:
            debug = tuple(
                (
                    file.id,
                    (
                        f"{file.relative_output_path} | "
                        f"owner={file.path_debug.owner_key if file.path_debug else None} "
                        f"owner_folders={file.path_debug.owner_folders if file.path_debug else ()} "
                        f"static={file.is_static} "
                        f"render_once={file.render_once} "
                        f"barrel={file.is_barrel}"
                    ),
                )
                for file in files[:25]
            )

        owner_folder_count = sum(
            1
            for file in files
            if file.path_debug is not None and file.path_debug.owner_folders
        )
        static_count = sum(1 for file in files if file.is_static)
        render_once_count = sum(1 for file in files if file.render_once)
        barrel_count = sum(1 for file in files if file.is_barrel)

        return success_result(
            state=replace(state, output_files=files),
            name=self.name,
            title=self.title,
            message="Output files planned.",
            started_at=started_at,
            counters=(
                ReportCounter("files", len(files)),
                ReportCounter("static_files", static_count),
                ReportCounter("render_once_files", render_once_count),
                ReportCounter("barrel_files", barrel_count),
                ReportCounter("owner_folder_paths", owner_folder_count),
            ),
            debug=debug,
        )