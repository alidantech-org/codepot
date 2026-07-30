from __future__ import annotations

import click

from dryv_cli.presentation import get_console, render_json, render_runtime
from dryv_cli.presentation.help import TreeHelpCommand
from dryv_cli.presentation.serialization import runtime_document

from .common import acquire_runtime


@click.command(
    "plugins",
    cls=TreeHelpCommand,
    help="Inspect the installed runtime plugin graph.",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Emit stable machine-readable JSON.",
)
def plugins_command(json_output: bool) -> None:
    runtime = acquire_runtime(json_output=json_output)
    snapshot = runtime.snapshot()
    console = get_console()
    if json_output:
        render_json(console, runtime_document(snapshot))
    else:
        render_runtime(console, snapshot)
