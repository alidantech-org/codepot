"""CLI console helpers."""

from __future__ import annotations

from rich.console import Console

console = Console(force_terminal=True)


def print_error(message: str) -> None:
    """Print an error message."""

    console.print(f"[red]X[/red] {message}")


def print_success(message: str) -> None:
    """Print a success message."""

    console.print(f"[green]OK[/green] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""

    console.print(f"[yellow]![/yellow] {message}")


def print_info(message: str) -> None:
    """Print an info message."""

    console.print(message)
