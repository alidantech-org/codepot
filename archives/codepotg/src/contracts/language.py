"""Shared language adapter contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from archives.codepotg.src.contracts.api import ApiContract
from archives.codepotg.src.contracts.emission import EmissionResult
from archives.codepotg.src.contracts.events import ProgressSink
from archives.codepotg.src.contracts.template import TemplateContract

Command = tuple[str, ...]


@dataclass(frozen=True)
class LanguagePostAction:
    """A post-emission action requested by a language adapter."""

    name: str
    command: Command = field(default_factory=tuple)
    working_directory: Path | None = None
    enabled: bool = True


@dataclass(frozen=True)
class LanguagePostResult:
    """Result of language post-actions."""

    actions: tuple[LanguagePostAction, ...] = ()
    diagnostics: tuple[str, ...] = ()


class LanguageAdapter(Protocol):
    """Protocol implemented by every language adapter."""

    name: str
    aliases: tuple[str, ...]
    template_name: str

    def build_template_contract(
        self,
        *,
        api: ApiContract,
        output_path: Path,
        template_root: Path | None = None,
        dry_run: bool = False,
        frontend: str | None = None,
        progress: ProgressSink | None = None,
    ) -> TemplateContract:
        """Build deterministic template variables for this language."""
        ...

    def after_emit(
        self,
        *,
        result: EmissionResult,
        progress: ProgressSink | None = None,
    ) -> LanguagePostResult:
        """Run optional language post-actions after emission."""
        ...
