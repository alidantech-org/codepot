from __future__ import annotations

from pathlib import Path

from dryv.api import CancellationToken, OperationResult, OperationStatus
from dryv.config import ConfigurationError, load_project
from dryv.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity
from dryv.generation import GenerationData
from dryv.runtime.plugins import PluginLoadError, RuntimePlugins
from dryv.runtime.session import GenerationSession


def generate(
    project_file: str | Path = "dryv.yaml",
    *,
    plugins: RuntimePlugins | None = None,
    cancellation: CancellationToken | None = None,
    dry_run: bool = False,
) -> OperationResult[GenerationData]:
    path = Path(project_file).resolve()
    try:
        project = load_project(path)
        if project.commands or any(pack.commands for pack in project.packs):
            raise ConfigurationError(
                "CMD_APPROVAL_REQUIRED",
                "project-owned commands require the separate approved command runtime",
                path="$.commands",
            )
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
