"""Interactive CLI prompts.

Questionary is imported lazily so non-interactive commands work even when
interactive dependencies are not installed.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, TypeVar, cast

from cli.constants.defaults import (
    DEFAULT_CONFIRM,
    DEFAULT_DRY_RUN,
    DEFAULT_INFERENCE_OUTPUT,
    DEFAULT_USE_CUSTOM_TEMPLATES,
    DEFAULT_WRITE_OUTPUT,
    LANGUAGE_CHOICES,
)
from cli.paths import normalize_cli_path

T = TypeVar("T")


def should_prompt(force: bool = False) -> bool:
    """Return whether CLI should ask interactive questions.

    Returns True if:
    - force is True (explicit --interactive flag), or
    - stdin is a TTY (interactive terminal)

    This allows commands to automatically prompt for missing required args
    when run interactively, while failing cleanly in non-interactive contexts.
    """
    return force or sys.stdin.isatty()


def ask_input_path() -> Path:
    """Ask for the input OpenAPI file path."""
    value = _ask(
        lambda q: q.path(
            "OpenAPI input file:",
            validate=lambda p: Path(p).exists() or "File does not exist",
        )
    )
    return normalize_cli_path(value) or Path(value)


def ask_language() -> str:
    """Ask for the target language."""
    return _ask(
        lambda q: q.select(
            "Target language:",
            choices=LANGUAGE_CHOICES,
            use_shortcuts=True,
        )
    )


def ask_output_path() -> Path:
    """Ask for the output directory or file path."""
    value = _ask(lambda q: q.path("Output path:"))
    return normalize_cli_path(value) or Path(value)


def ask_optional_output_path() -> Path | None:
    """Ask whether to write optional output."""
    questionary = _load_questionary()
    should_write = questionary.confirm(
        "Write output file?",
        default=DEFAULT_WRITE_OUTPUT,
    ).ask()

    if not should_write:
        return None

    value = questionary.path(
        "Output file:",
        default=DEFAULT_INFERENCE_OUTPUT,
    ).ask()

    if not value:
        return None

    return normalize_cli_path(value) or Path(value)


def ask_templates_path() -> Path | None:
    """Ask whether to use a custom template path."""
    use_custom = _ask(lambda q: q.confirm("Use custom templates?", default=DEFAULT_USE_CUSTOM_TEMPLATES))

    if not use_custom:
        return None

    value = _ask(lambda q: q.path("Templates path:"))
    return normalize_cli_path(value) or Path(value)


def ask_dry_run() -> bool:
    """Ask whether emit should run as dry-run."""
    return _ask(lambda q: q.confirm("Dry run only?", default=DEFAULT_DRY_RUN))


def ask_confirm(message: str, *, default: bool = DEFAULT_CONFIRM) -> bool:
    """Ask a yes/no confirmation question."""
    return _ask(lambda q: q.confirm(message, default=default))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _ask(prompt_factory: Callable[[Any], Any]) -> T:
    """Run a questionary prompt and raise on empty/cancelled input."""
    q = _load_questionary()
    value = prompt_factory(q).ask()

    if value is None:
        raise KeyboardInterrupt("prompt cancelled")

    if isinstance(value, str) and not value.strip():
        raise ValueError("a value is required")

    return cast(T, value)


def _load_questionary():
    try:
        import questionary
    except ImportError as exc:
        raise RuntimeError("Interactive mode requires 'questionary'. Install it with: pip install questionary") from exc

    return questionary
