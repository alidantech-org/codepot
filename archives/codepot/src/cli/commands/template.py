"""Template package commands."""

from __future__ import annotations

from pathlib import Path

import typer

from archives.codepot.src.app import codepotx
from archives.codepot.src.cli.presentation.console import print_error
from archives.codepot.src.cli.presentation.template import print_template_validation_result

app = typer.Typer(help="Template package commands.")

TEMPLATE_PATH_ARGUMENT = typer.Argument(..., help="Template package path.")


@app.command("validate")
def validate_template(
    template_package_path: Path = TEMPLATE_PATH_ARGUMENT,
) -> None:
    """Validate a codepotx template package."""

    try:
        result = codepotx.validate_template_package(template_package_path)
    except Exception as error:
        print_error(str(error))
        raise typer.Exit(code=1) from error

    print_template_validation_result(result)

    if not result.is_valid:
        raise typer.Exit(code=1)

 
@app.command("vars")
def template_vars() -> None:
    """List template variables."""

    try:
        codepotx.template_vars()
    except NotImplementedError as error:
        print_error(str(error))
        raise typer.Exit(code=2) from error


@app.command("selections")
def template_selections() -> None:
    """List template selections."""

    try:
        codepotx.template_selections()
    except NotImplementedError as error:
        print_error(str(error))
        raise typer.Exit(code=2) from error
