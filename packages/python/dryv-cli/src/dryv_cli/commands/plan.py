from __future__ import annotations

from pathlib import Path

import click

from dryv_cli.presentation import activity
from dryv_cli.presentation.help import TreeHelpCommand

from .common import acquire_runtime, emit_result


@click.command(
    "plan",
    cls=TreeHelpCommand,
    help="Validate the project and display the complete artifact plan.",
)
@click.argument(
    "project",
    required=False,
    default="dryv.yaml",
    type=click.Path(path_type=Path, dir_okay=False),
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Emit stable machine-readable JSON without interactive output.",
)
def plan_command(project: Path, json_output: bool) -> None:
    runtime = acquire_runtime(json_output=json_output)
    with activity("Planning project", enabled=not json_output):
        result = runtime.plan(project)
    emit_result(result, json_output=json_output)
