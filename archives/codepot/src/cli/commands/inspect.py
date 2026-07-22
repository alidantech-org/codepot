"""Inspect command."""

from __future__ import annotations

import typer

from archives.codepot.src.app import codepotx
from archives.codepot.src.cli.options import InspectModeOption, SpecPathArg
from archives.codepot.src.cli.presentation.console import print_error
from archives.codepot.src.cli.presentation.inspect import print_inspect_result


def inspect_command(
    spec_path: SpecPathArg,
    mode: InspectModeOption = "overview",
) -> None:
    """Inspect a compiled Codepot spec."""

    try:
        context = codepotx.inspect(spec_path)
    except Exception as error:
        print_error(str(error))
        raise typer.Exit(code=1) from error

    print_inspect_result(context, mode)
