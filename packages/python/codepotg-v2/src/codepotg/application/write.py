from __future__ import annotations

from pathlib import Path

from codepotg.api import CancellationToken, OperationResult, OperationStatus
from codepotg.diagnostics import Diagnostic, DiagnosticSeverity
from codepotg.generation import GenerationData
from codepotg.infrastructure import ManagedFilesystemWriter, ManagedWriteReport
from codepotg.runtime.plugins import RuntimePlugins

from .generate import generate


def generate_to_files(
    project_file: str | Path = "codepotg.yaml",
    *,
    destination: str | Path | None = None,
    plugins: RuntimePlugins | None = None,
    cancellation: CancellationToken | None = None,
) -> tuple[OperationResult[GenerationData], ManagedWriteReport | None]:
    result = generate(
        project_file,
        plugins=plugins,
        cancellation=cancellation,
        dry_run=False,
    )
    if not result.ok or result.data is None or result.data.output is None:
        return result, None

    project_path = Path(project_file).resolve()
    root = Path(destination).resolve() if destination is not None else project_path.parent
    try:
        report = ManagedFilesystemWriter().write(result.data.output, root)
    except (OSError, ValueError) as exc:
        diagnostic = Diagnostic(
            code="WRITE_FAILED",
            severity=DiagnosticSeverity.ERROR,
            message="generated output could not be committed with ownership safety",
            details=(
                ("exception_type", type(exc).__name__),
                ("reason", str(exc)),
                ("root", str(root)),
            ),
        )
        failed = OperationResult(
            status=OperationStatus.FAILED,
            data=result.data,
            diagnostics=result.diagnostics.add(diagnostic),
            operation_id=result.operation_id,
            metadata=result.metadata,
        )
        return failed, None
    return result, report
