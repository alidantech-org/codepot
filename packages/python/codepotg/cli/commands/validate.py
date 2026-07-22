from __future__ import annotations

from pathlib import Path

import typer

from cli.constants.constants import (
    HELP_DEBUG,
    HELP_INPUT,
    HELP_INTERACTIVE,
    HELP_QUIET,
    HELP_VERBOSE,
    OPT_DEBUG,
    OPT_INPUT,
    OPT_INTERACTIVE,
    OPT_QUIET,
    OPT_VERBOSE,
)
from cli.presentation.core.console import print_error, print_header
from cli.presentation.core.interactive import ask_input_path, should_prompt
from cli.presentation.validate.renderer import render_validate_result


def validate_command(
    ctx: typer.Context,
    input_file: Path | None = typer.Option(
        None,
        f"--{OPT_INPUT}",
        "-i",
        help=HELP_INPUT,
        exists=False,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    interactive: bool = typer.Option(
        False,
        f"--{OPT_INTERACTIVE}",
        "-I",
        help=HELP_INTERACTIVE,
    ),
    debug: bool = typer.Option(False, f"--{OPT_DEBUG}", help=HELP_DEBUG),
    verbose: bool = typer.Option(False, f"--{OPT_VERBOSE}", "-v", help=HELP_VERBOSE),
    quiet: bool = typer.Option(False, f"--{OPT_QUIET}", "-q", help=HELP_QUIET),
) -> None:
    """Validate an OpenAPI document."""
    try:
        from cli.main import get_runtime

        resolved_input = input_file

        prompt = should_prompt(interactive)

        if resolved_input is None and prompt:
            resolved_input = ask_input_path()

        if resolved_input is None:
            raise ValueError("missing required option: --input")

        if not quiet:
            print_header("Validate", str(resolved_input))

        runtime = get_runtime(ctx)
        result = runtime.validate(input_path=resolved_input)

        if not quiet:
            render_validate_result(result, verbose=verbose)

    except Exception as exc:
        print_error(str(exc))
        if debug:
            raise
        raise typer.Exit(1) from exc
