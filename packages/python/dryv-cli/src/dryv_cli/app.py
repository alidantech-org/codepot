from __future__ import annotations

import click
from dryv import __version__ as runtime_version
from rich.text import Text

from dryv_cli import __version__
from dryv_cli.commands import generate_command, plan_command, plugins_command
from dryv_cli.presentation import get_console
from dryv_cli.presentation.help import TreeHelpGroup


@click.group(
    cls=TreeHelpGroup,
    invoke_without_command=True,
    context_settings={
        "help_option_names": ["-h", "--help"],
        "max_content_width": 100,
    },
    help="Plan, inspect, and generate projects through the Dryv runtime.",
)
@click.option("--version", is_flag=True, help="Show CLI and runtime versions.")
@click.pass_context
def app(ctx: click.Context, version: bool) -> None:
    if version:
        line = Text()
        line.append("dryv-cli", style="accent")
        line.append(f" {__version__}", style="value")
        line.append("  runtime ", style="muted")
        line.append(runtime_version, style="value")
        get_console().print(line)
        raise click.exceptions.Exit(0)

    if ctx.invoked_subcommand is None:
        get_console().print(Text.from_ansi(ctx.get_help()))


app.add_command(plan_command)
app.add_command(generate_command)
app.add_command(plugins_command)
