from __future__ import annotations

from contextlib import nullcontext
from typing import ContextManager

from rich.console import Console
from rich.status import Status

from .theme import DRYV_THEME

_CONSOLE = Console(theme=DRYV_THEME, highlight=False)


def get_console() -> Console:
    return _CONSOLE


def activity(message: str, *, enabled: bool = True) -> ContextManager[Status | None]:
    if not enabled:
        return nullcontext()
    return _CONSOLE.status(f"[accent]{message}[/]", spinner="dots")
