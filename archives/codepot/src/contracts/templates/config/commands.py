"""Template package command/message config contracts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TemplateCommandsConfig(BaseModel):
    """Named shell commands suggested or run by explicit CLI flags."""

    model_config = ConfigDict(frozen=True)

    install: str | None = None
    format: str | None = None
    lint: str | None = None
    typecheck: str | None = None
    test: str | None = None


class TemplateMessagesConfig(BaseModel):
    """Template package user-facing messages."""

    model_config = ConfigDict(frozen=True)

    success: tuple[str, ...] = ()
    next_steps: tuple[str, ...] = ()
