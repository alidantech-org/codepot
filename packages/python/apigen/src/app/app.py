"""Public runtime application API."""

from __future__ import annotations

from pathlib import Path

from app.models import (
    EmitInput,
    EmitOutput,
    GenerateInput,
    GenerateOutput,
    InferInput,
    InferOutput,
    InspectInput,
    InspectOutput,
    ProgressSink,
    ValidateInput,
    ValidateOutput,
)
from app.workflows.emit import run_emit
from app.workflows.generate import run_generate
from app.workflows.infer import run_infer
from app.workflows.inspect import run_inspect
from app.workflows.validate import run_validate


class GeneratorApp:
    """Public runtime API for the generator.

    Interfaces such as CLI, UI, tests, or HTTP handlers should call this class.
    Runtime methods return structured results and do not render terminal output.
    """

    def inspect(self, input_path: Path) -> InspectOutput:
        """Inspect an OpenAPI document."""
        return run_inspect(
            InspectInput(
                input_path=input_path,
            )
        )

    def infer(
        self,
        input_path: Path,
        output_path: Path | None = None,
    ) -> InferOutput:
        """Run OpenAPI inference."""
        return run_infer(
            InferInput(
                input_path=input_path,
                output_path=output_path,
            )
        )

    def emit(
        self,
        input_path: Path,
        language: str,
        output_path: Path,
        *,
        dry_run: bool = False,
        templates_path: Path | None = None,
    ) -> EmitOutput:
        """Emit generated output for a language."""
        return run_emit(
            EmitInput(
                input_path=input_path,
                language=language,
                output_path=output_path,
                dry_run=dry_run,
                templates_path=templates_path,
            )
        )

    def generate(
        self,
        *,
        config_path: Path | None = None,
        task_name: str | None = None,
        all_tasks: bool = False,
        dry_run: bool = False,
        verbose: bool = False,
        refresh: bool = False,
        skip_before: bool = False,
        skip_after: bool = False,
        progress: ProgressSink | None = None,
    ) -> GenerateOutput:
        """Run CodepotFile-driven generation."""
        return run_generate(
            GenerateInput(
                config_path=config_path,
                task_name=task_name,
                all_tasks=all_tasks,
                dry_run=dry_run,
                verbose=verbose,
                refresh=refresh,
                skip_before=skip_before,
                skip_after=skip_after,
                progress=progress,
            )
        )

    def validate(self, input_path: Path) -> ValidateOutput:
        """Validate an OpenAPI document."""
        return run_validate(
            ValidateInput(
                input_path=input_path,
            )
        )
