from __future__ import annotations

import click
from rich.text import Text

from dryv_cli import __version__
from dryv_cli.commands import build_command
from dryv_cli.presentation import get_console
from dryv_cli.presentation.help import TreeHelpGroup


@click.group(
    cls=TreeHelpGroup,
    invoke_without_command=True,
    context_settings={
        "help_option_names": ["-h", "--help"],
        "max_content_width": 100,
    },
    help="Build Dryv projects through the versioned Dryv API and apply artifacts locally.",
)
@click.option("--version", is_flag=True, help="Show the CLI version.")
@click.pass_context
def app(ctx: click.Context, version: bool) -> None:
    if version:
        line = Text()
        line.append("dryv-cli", style="accent")
        line.append(f" {__version__}", style="value")
        get_console().print(line)
        raise click.exceptions.Exit(0)

    if ctx.invoked_subcommand is None:
        get_console().print(Text.from_ansi(ctx.get_help()))


app.add_command(build_command)
