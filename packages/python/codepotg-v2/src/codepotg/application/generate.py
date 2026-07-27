from __future__ import annotations

from pathlib import Path

from codepotg.api import CancellationToken, OperationResult, OperationStatus
from codepotg.config import ConfigurationError, load_project
from codepotg.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity
from codepotg.generation import GenerationData
from codepotg.runtime import GenerationSession, PluginLoadError, RuntimePlugins


def generate(
    project_file: str | Path = "codepotg.yaml",
    *,
    plugins: RuntimePlugins | None = None,
    cancellation: CancellationToken | None = None,
    dry_run: bool = False,
) -> OperationResult[GenerationData]:
    path = Path(project_file).resolve()
    try:
        project = load_project(path)
        runtime_plugins = plugins or RuntimePlugins.discover()
    except (ConfigurationError, PluginLoadError, OSError, ValueError) as exc:
        code = getattr(exc, "code", "GENERATION_SETUP_FAILED")
        message = getattr(exc, "message", None) or str(exc) or "generation setup failed"
        diagnostics = Diagnostics(
            (
                Diagnostic(
                    code=code,
                    severity=DiagnosticSeverity.ERROR,
                    message=message,
                    details=(("project_file", str(path)),),
                ),
            )
        )
        return OperationResult(
            status=OperationStatus.FAILED,
            diagnostics=diagnostics,
        )

    return GenerationSession(runtime_plugins).generate(
        project=project,
        project_root=path.parent,
        cancellation=cancellation,
        dry_run=dry_run,
    )
