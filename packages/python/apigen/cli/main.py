# ruff: noqa: E402, I001

from __future__ import annotations

from typing import Protocol

from cli.bootstrap import ensure_src_on_path

ensure_src_on_path()

import typer

from app import GeneratorApp

from cli.commands.generate import generate_command
from cli.constants.constants import (
    APP_DESCRIPTION,
    APP_NAME,
    CMD_GENERATE,
    HELP_GENERATE,
)

RUNTIME_KEY = "runtime"


class RuntimeApi(Protocol):
    """Runtime methods the CLI is allowed to call."""

    def generate(self, **kwargs):
        """Run CodepotFile generation."""


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
    rich_markup_mode="rich",
)


@app.callback()
def main(ctx: typer.Context) -> None:
    """Initialize CLI runtime state."""
    set_runtime(ctx, GeneratorApp())


app.command(CMD_GENERATE, help=HELP_GENERATE)(generate_command)


if __name__ == "__main__":
    app()
