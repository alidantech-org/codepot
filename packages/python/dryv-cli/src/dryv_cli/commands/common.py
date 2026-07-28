from __future__ import annotations

import click
from dryv.api import OperationResult
from dryv.generation import GenerationData
from dryv.ports import ManagedWriteReport
from dryv.runtime import DryvRuntime, PluginLoadError

from dryv_cli.presentation import activity, get_console, render_failure, render_json, render_operation
from dryv_cli.presentation.serialization import result_document
from dryv_cli.services import load_runtime, operation_exit_code


def acquire_runtime(*, json_output: bool) -> DryvRuntime:
    console = get_console()
    try:
        with activity("Loading Dryv runtime", enabled=not json_output):
            return load_runtime()
    except PluginLoadError as exc:
        if json_output:
            render_json(
                console,
                {
                    "status": "failed",
                    "diagnostics": (
                        {
                            "code": "PLUGIN_LOAD_FAILED",
                            "severity": "error",
                            "message": str(exc),
                        },
                    ),
                },
            )
        else:
            render_failure(console, str(exc), code="PLUGIN_LOAD_FAILED")
        raise click.exceptions.Exit(1) from exc


def emit_result(
    result: OperationResult[GenerationData],
    *,
    report: ManagedWriteReport | None = None,
    json_output: bool,
) -> None:
    console = get_console()
    if json_output:
        render_json(console, result_document(result, report=report))
    else:
        render_operation(console, result, report=report)
    raise click.exceptions.Exit(operation_exit_code(result.status))
