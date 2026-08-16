from __future__ import annotations

import sys
from pathlib import Path

import questionary
from questionary import Style

_PROMPT_STYLE = Style(
    [
        ("qmark", "fg:#00d7ff bold"),
        ("question", "bold"),
        ("answer", "fg:#00d787 bold"),
        ("pointer", "fg:#00d7ff bold"),
        ("highlighted", "fg:#00d7ff bold"),
    ]
)


def can_prompt() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def confirm_generation(
    *,
    project_name: str,
    artifact_count: int,
    destination: str | Path | None,
) -> bool:
    target = str(destination) if destination is not None else "the project output roots"
    answer = questionary.confirm(
        f"Write {artifact_count} planned artifacts for {project_name} to {target}?",
        default=True,
        qmark="›",
        style=_PROMPT_STYLE,
    ).ask()
    return bool(answer)
