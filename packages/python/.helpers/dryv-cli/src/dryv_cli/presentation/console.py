from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext

from rich.console import Console
from rich.status import Status

from .theme import DRYV_THEME

_CONSOLE = Console(theme=DRYV_THEME, highlight=False)


def get_console() -> Console:
    return _CONSOLE


def activity(message: str, *, enabled: bool = True) -> AbstractContextManager[Status | None]:
    if not enabled:
        return nullcontext()
    return _CONSOLE.status(f"[accent]{message}[/]", spinner="dots")
