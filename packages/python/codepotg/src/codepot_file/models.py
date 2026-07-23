"""Internal data models for CodepotG configuration and task execution."""

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
    """A config-driven CodepotG generation task."""

    name: str
    input: Path
    language: str
    output: Path
    template_dir: Path | None = None
    clean: tuple[Path, ...] = ()
    before: tuple[CodepotCommand, ...] = ()
    after: tuple[CodepotCommand, ...] = ()
    env: dict[str, str] = field(default_factory=dict)
    description: str = ""
    frontend: str | None = None


@dataclass(frozen=True)
class CodepotFile:
    """Loaded ``Codepotg.yaml`` configuration.

    The class name is retained internally while the package moves away from the
    old shared CodepotFile filename. Consumers interact with ``Codepotg.yaml``.
    """

    path: Path
    root: Path
    allow: bool
    defaults: dict[str, object]
    tasks: tuple[CodepotTask, ...]
