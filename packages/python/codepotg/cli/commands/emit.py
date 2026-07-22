from __future__ import annotations

from pathlib import Path

import typer

from cli.constants.constants import (
    HELP_DEBUG,
    HELP_DRY_RUN,
    HELP_INPUT,
    HELP_INTERACTIVE,
    HELP_LANGUAGE,
    HELP_OUTPUT,
    HELP_QUIET,
    HELP_TEMPLATES_PATH,
    HELP_VERBOSE,
    OPT_DEBUG,
    OPT_DRY_RUN,
    OPT_INPUT,
    OPT_INTERACTIVE,
    OPT_LANGUAGE,
    OPT_OUTPUT,
    OPT_QUIET,
    OPT_TEMPLATES,
    OPT_VERBOSE,
)
from cli.presentation.core.console import print_error, print_header
from cli.presentation.core.interactive import (
    ask_dry_run,
    ask_input_path,
    ask_language,
    ask_output_path,
    ask_templates_path,
    should_prompt,
)
from cli.paths import normalize_cli_path
from cli.presentation.emit.renderer import render_emit_result


def emit_command(
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
    language: str | None = typer.Option(
        None,
        f"--{OPT_LANGUAGE}",
        "-l",
        help=HELP_LANGUAGE,
    ),
    output: Path | None = typer.Option(
        None,
        f"--{OPT_OUTPUT}",
        "-o",
        help=HELP_OUTPUT,
    ),
    templates_path: Path | None = typer.Option(
        None,
        f"--{OPT_TEMPLATES}",
        "-t",
        help=HELP_TEMPLATES_PATH,
    ),
    dry_run: bool = typer.Option(False, f"--{OPT_DRY_RUN}", help=HELP_DRY_RUN),
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
    """Emit output for a target language."""
    try:
        from cli.main import get_runtime

        resolved_input = input_file
        resolved_language = language
        resolved_output = output
        resolved_templates_path = templates_path
        resolved_dry_run = dry_run

        prompt = should_prompt(interactive)

        if resolved_input is None and prompt:
            resolved_input = ask_input_path()

        if resolved_language is None and prompt:
            resolved_language = ask_language()

        if resolved_output is None and prompt:
            resolved_output = ask_output_path()

        if resolved_templates_path is None and interactive:
            resolved_templates_path = ask_templates_path()

        if not dry_run and interactive:
            resolved_dry_run = ask_dry_run()

        if resolved_input is None:
            raise ValueError("missing required option: --input")
        if resolved_language is None:
            raise ValueError("missing required option: --language")
        if resolved_output is None:
            raise ValueError("missing required option: --output")

        resolved_input = normalize_cli_path(resolved_input)
        resolved_output = normalize_cli_path(resolved_output)
        resolved_templates_path = normalize_cli_path(resolved_templates_path)

        if not quiet:
            print_header("Emit", f"{resolved_language} -> {resolved_output}")

        runtime = get_runtime(ctx)
        result = runtime.emit(
            input_path=resolved_input,
            language=resolved_language,
            output_path=resolved_output,
            dry_run=resolved_dry_run,
            templates_path=resolved_templates_path,
        )

        if not quiet:
            render_emit_result(result, verbose=verbose)

    except Exception as exc:
        print_error(str(exc))
        if debug:
            raise
        raise typer.Exit(1) from exc
