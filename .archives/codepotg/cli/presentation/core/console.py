"""Shared Rich console helpers for CLI presentation."""

from __future__ import annotations

from rich.console import Console

console = Console()
error_console = Console(stderr=True)

# Palette aligned with tables.py and diagnostics.py
_RED = "#E24B4A"
_AMBER = "#EF9F27"
_BLUE = "#378ADD"
_GREEN = "#1D9E75"
_PURPLE = "#7F77DD"


def print_header(title: str, detail: str | None = None) -> None:
    """Print a styled section rule with an optional detail annotation."""
    label = f"[bold {_PURPLE}]{title}[/bold {_PURPLE}]"
    if detail:
        label += f"  [dim]{detail}[/dim]"
    console.rule(label, style="bright_black")


def print_subheader(title: str) -> None:
    """Print a lighter secondary heading (no rule line)."""
    console.print(f"\n[bold {_BLUE}]> {title}[/bold {_BLUE}]")


def print_error(message: str) -> None:
    """Print a styled error to stderr."""
    error_console.print(f"[{_RED}]x error:[/{_RED}] {message}")


def print_success(message: str) -> None:
    """Print a styled success message."""
    console.print(f"[{_GREEN}]+[/{_GREEN}] {message}")


def print_warning(message: str) -> None:
    """Print a styled warning message."""
    console.print(f"[{_AMBER}]! warning:[/{_AMBER}] {message}")


def print_info(message: str) -> None:
    """Print a styled informational message."""
    console.print(f"[{_BLUE}]i[/{_BLUE}] [dim]{message}[/dim]")


def print_step(index: int, total: int, message: str) -> None:
    """Print a numbered progress step, e.g. during a multi-stage pipeline."""
    counter = f"[dim]{index}/{total}[/dim]"
    console.print(f"  {counter}  {message}")


def print_blank() -> None:
    """Print an empty line for vertical rhythm."""
    console.print()
