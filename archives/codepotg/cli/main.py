# ruff: noqa: E402, I001

from __future__ import annotations

from typing import Protocol

from archives.codepotg.cli.bootstrap import ensure_src_on_path

ensure_src_on_path()

import typer

from app import GeneratorApp

from archives.codepotg.cli.commands.generate import generate_command
from archives.codepotg.cli.commands.init import init_command
from archives.codepotg.cli.commands.jsonl import jsonl_command
from archives.codepotg.cli.commands.paths import paths_command
from archives.codepotg.cli.commands.task import app as task_app
from archives.codepotg.cli.constants.constants import (
    APP_DESCRIPTION,
    APP_NAME,
    APP_VERSION,
    CMD_GENERATE,
    CMD_INIT,
    CMD_JSONL,
    CMD_PATHS,
    CMD_TASK,
    HELP_GENERATE,
    HELP_INIT,
    HELP_JSONL,
    HELP_PATHS,
    HELP_TASK,
    HELP_VERSION,
)

RUNTIME_KEY = "runtime"


class RuntimeApi(Protocol):
    """Runtime methods the CLI is allowed to call."""

    def generate(self, **kwargs):
        """Run CodepotG configuration-driven generation."""

    def jsonl(self, *args, **kwargs):
        """Compile a visible indexed JSONL cache."""

    def paths(self, *args, **kwargs):
        """Resolve and inspect a paths configuration."""


def set_runtime(ctx: typer.Context, runtime: RuntimeApi) -> None:
    """Store runtime instance in Typer context."""
    if ctx.obj is None:
        ctx.obj = {}

    ctx.obj[RUNTIME_KEY] = runtime


def get_runtime(ctx: typer.Context) -> RuntimeApi:
    """Get runtime instance from Typer context."""
    if ctx.obj is None or RUNTIME_KEY not in ctx.obj:
        raise RuntimeError("CLI runtime was not initialized.")

    return ctx.obj[RUNTIME_KEY]


app = typer.Typer(
    name=APP_NAME,
    help=APP_DESCRIPTION,
    add_completion=False,
    no_args_is_help=True,
    invoke_without_command=True,
    rich_markup_mode="rich",
)


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        help=HELP_VERSION,
        is_eager=True,
    ),
) -> None:
    """Initialize CLI runtime state."""
    if version:
        typer.echo(f"{APP_NAME} {APP_VERSION}")
        raise typer.Exit()

    set_runtime(ctx, GeneratorApp())


app.command(CMD_GENERATE, help=HELP_GENERATE)(generate_command)
app.command(CMD_INIT, help=HELP_INIT)(init_command)
app.command(CMD_JSONL, help=HELP_JSONL)(jsonl_command)
app.command(CMD_PATHS, help=HELP_PATHS)(paths_command)
app.add_typer(task_app, name=CMD_TASK, help=HELP_TASK)


if __name__ == "__main__":
    app()
