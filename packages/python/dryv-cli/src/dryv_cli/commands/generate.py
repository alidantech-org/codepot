from __future__ import annotations

from pathlib import Path

import click

from dryv_cli.presentation import (
    activity,
    get_console,
    render_cancelled,
    render_failure,
    render_operation,
)
from dryv_cli.presentation.help import TreeHelpCommand
from dryv_cli.prompts import can_prompt, confirm_generation

from .common import acquire_runtime, emit_result


@click.command(
    "generate",
    cls=TreeHelpCommand,
    help="Render the project in memory or transactionally write managed files.",
)
@click.argument(
    "project",
    required=False,
    default="dryv.yaml",
    type=click.Path(path_type=Path, dir_okay=False),
)
@click.option(
    "--destination",
    type=click.Path(path_type=Path, file_okay=False),
    default=None,
    help="Override the managed output root.",
)
@click.option(
    "--memory",
    is_flag=True,
    help="Render in memory without writing files.",
)
@click.option(
    "--confirm",
    "confirm_write",
    is_flag=True,
    help="Require an interactive confirmation before writing.",
)
@click.option(
    "--yes",
    is_flag=True,
    help="Skip the normal interactive confirmation.",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Emit stable machine-readable JSON and never prompt.",
)
def generate_command(
    project: Path,
    destination: Path | None,
    memory: bool,
    confirm_write: bool,
    yes: bool,
    json_output: bool,
) -> None:
    if memory and destination is not None:
        raise click.UsageError("--destination cannot be used with --memory")
    if confirm_write and yes:
        raise click.UsageError("--confirm and --yes cannot be used together")

    runtime = acquire_runtime(json_output=json_output)

    if memory:
        with activity("Rendering in memory", enabled=not json_output):
            result = runtime.generate(project)
        emit_result(result, json_output=json_output)

    interactive = can_prompt()
    should_confirm = not json_output and not yes and (confirm_write or interactive)
    if confirm_write and not interactive:
        render_failure(
            get_console(),
            "Interactive confirmation is unavailable. Re-run with --yes.",
            code="PROMPT_UNAVAILABLE",
        )
        raise click.exceptions.Exit(2)

    if should_confirm:
        with activity("Preparing confirmation plan"):
            plan_result = runtime.plan(project)
        if not plan_result.ok or plan_result.data is None:
            emit_result(plan_result, json_output=False)

        render_operation(get_console(), plan_result)
        approved = confirm_generation(
            project_name=plan_result.data.plan.project_name,
            artifact_count=len(plan_result.data.plan.artifacts),
            destination=destination,
        )
        if not approved:
            render_cancelled(get_console())
            raise click.exceptions.Exit(0)

    with activity("Generating managed output", enabled=not json_output):
        result, report = runtime.generate_to_files(project, destination=destination)
    emit_result(result, report=report, json_output=json_output)
