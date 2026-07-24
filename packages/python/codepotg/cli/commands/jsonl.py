# ruff: noqa: B008

from __future__ import annotations

from pathlib import Path

import typer

from cli.paths import normalize_cli_path
from cli.presentation.core.console import (
    print_error,
    print_header,
    print_info,
    print_success,
)
from cli.presentation.core.reporter import Reporter
from cli.presentation.emit.files import render_emit_files

DEFAULT_JSONL_CACHE = Path(".codepotg/cache/openapi")


def jsonl_command(
    ctx: typer.Context,
    input_path: Path = typer.Argument(
        ...,
        help="Input OpenAPI JSON document.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    output_path: Path = typer.Option(
        DEFAULT_JSONL_CACHE,
        "--output",
        "-o",
        help="Visible JSONL cache directory.",
        file_okay=False,
        dir_okay=True,
    ),
    refresh: bool = typer.Option(
        False,
        "--refresh",
        "-r",
        help="Recompile even when the source hash is unchanged.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show every generated JSONL and index file.",
    ),
    debug: bool = typer.Option(False, "--debug", help="Show traceback on failure."),
) -> None:
    """Compile OpenAPI JSON into indexed JSONL files."""
    try:
        from cli.main import get_runtime

        resolved_input = normalize_cli_path(input_path)
        resolved_output = normalize_cli_path(output_path)
        if resolved_input is None or resolved_output is None:
            raise ValueError("JSONL input and output paths are required.")

        reporter = Reporter(verbose=verbose)
        print_header("JSONL", str(resolved_input))
        result = get_runtime(ctx).jsonl(
            resolved_input,
            resolved_output,
            reuse_unchanged=not refresh,
            progress=reporter.event,
        )

        reporter.step("Summary")
        print_success(
            f"{'Reused' if result.reused else 'Compiled'} JSONL cache: {result.output_path}"
        )
        print_info(f"Records: {result.records}")
        print_info(
            "Indexes: "
            f"{result.definitions} definitions, "
            f"{result.mentions} mentions, "
            f"{result.dependencies} dependencies"
        )
        print_info(
            "Queue peaks: "
            f"{result.record_queue_high_water} records, "
            f"{result.pending_bytes_high_water} pending bytes, "
            f"{result.event_queue_high_water} events"
        )

        if verbose:
            render_emit_files("JSONL Cache Files", result.files)
        else:
            print_info(f"Files: {len(result.files)} (use --verbose to list them)")
    except Exception as exc:
        print_error(str(exc))
        if debug:
            raise
        raise typer.Exit(1) from exc
