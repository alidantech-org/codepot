"""Codepotx CLI entrypoint."""

from __future__ import annotations

import typer

from archives.codepot.src.cli.commands.emit import emit_command
from archives.codepot.src.cli.commands.infer import plan_command
from archives.codepot.src.cli.commands.inspect import inspect_command
from archives.codepot.src.cli.commands.template import app as template_app
from archives.codepot.src.cli.commands.validate import validate_command

app = typer.Typer(
    name="cpx-old",
    help="Legacy Codepotx code generation CLI.",
    no_args_is_help=True,
)

app.command("validate")(validate_command)
app.command("inspect")(inspect_command)
app.command("plan")(plan_command)
app.command("emit")(emit_command)

app.add_typer(template_app, name="template")


def main() -> None:
    """Run CLI."""

    app()


if __name__ == "__main__":
    main()
