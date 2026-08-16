from __future__ import annotations

import json
import os
import shlex
import sys
from pathlib import Path

import click

from dryv_cli.api_stdio import ApiTransportError, StdioApiTransport
from dryv_cli.project_client import ProjectClientError, apply_build_events
from dryv_cli.presentation.help import TreeHelpCommand


@click.command(
    "build",
    cls=TreeHelpCommand,
    help="Send a versioned Dryv API build request and apply returned artifacts locally.",
)
@click.argument("request", type=click.Path(path_type=Path, dir_okay=False, exists=True))
@click.option(
    "--root",
    type=click.Path(path_type=Path, file_okay=False),
    default=Path("."),
    show_default=True,
    help="Local Project Client root. This path is never sent to Dryv Runtime.",
)
@click.option(
    "--api-command",
    default=None,
    help="Command used to start/connect the Dryv API host. Defaults to DRYV_API_COMMAND or python -m dryv_api.stdio.",
)
@click.option("--json", "json_output", is_flag=True, help="Emit the final apply acknowledgement as JSON.")
def build_command(
    request: Path,
    root: Path,
    api_command: str | None,
    json_output: bool,
) -> None:
    try:
        document = json.loads(request.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise click.ClickException(f"build request is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise click.ClickException("build request root must be a JSON object")

    command_value = api_command or os.environ.get("DRYV_API_COMMAND")
    command = (
        tuple(shlex.split(command_value))
        if command_value
        else (sys.executable, "-m", "dryv_api.stdio")
    )
    if not command:
        raise click.ClickException("Dryv API command is empty")

    try:
        with StdioApiTransport(command) as api:
            events = tuple(api.build_events(document))
        acknowledgement = apply_build_events(root, events)
    except (ApiTransportError, ProjectClientError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc

    if json_output:
        click.echo(json.dumps(acknowledgement, sort_keys=True, separators=(",", ":")))
        return

    if acknowledgement.get("applyComplete"):
        click.echo(
            f"Applied Dryv build {acknowledgement.get('buildId')} to {root.resolve()}"
        )
    else:
        click.echo(
            f"Dryv build {acknowledgement.get('buildId')} was not applied; renderComplete={acknowledgement.get('renderComplete')}"
        )


__all__ = ["build_command"]
