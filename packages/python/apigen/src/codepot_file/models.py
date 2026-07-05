"""CodepotFile data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class CodepotCommand:
    """A user-defined shell command."""

    name: str | None
    run: str
    cwd: Path | None = None
    optional: bool = False
    env: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class CodepotTask:
    """A config-driven generation task."""

    name: str
    input: Path
    language: str
    output: Path
    template_dir: Path
    clean: tuple[Path, ...] = ()
    before: tuple[CodepotCommand, ...] = ()
    after: tuple[CodepotCommand, ...] = ()
    env: dict[str, str] = field(default_factory=dict)
    description: str = ""


@dataclass(frozen=True)
class CodepotFile:
    """Loaded CodepotFile config."""

    path: Path
    root: Path
    allow: bool
    defaults: dict[str, object]
    tasks: tuple[CodepotTask, ...]
