"""Shared emission contracts.

Emission consumes TemplateContract and produces plans/results. It does not know
about concrete language implementations, OpenAPI documents, or inference.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from contracts.paths import PathLifecycleMode

TemplateContext = Mapping[str, Any]


@dataclass(frozen=True)
class EmissionFile:
    """One planned or rendered output file."""

    template_path: Path
    output_path: Path
    context: TemplateContext
    content: str | bytes | None = None
    group: str = "global"
    is_template: bool = True
    compare_mode: str = "exact"
    lifecycle: PathLifecycleMode = PathLifecycleMode.MANAGED
    folder_key: str = "global"
    refusal_reason: str = ""
    node_key: str = ""
    selection: str = ""
    source_key: str = ""
    source_ref: str | None = None
    resource: str | None = None
    provides: tuple[str, ...] = ()
    provided_symbols: tuple[str, ...] = ()
    providers: Mapping[str, str] = field(default_factory=dict)
    depends_on: tuple[str, ...] = ()
    dependency_outputs: Mapping[str, str] = field(default_factory=dict)
    is_barrel: bool = False

    @property
    def identity(self) -> str:
        """Stable graph identity used before and after physical writing."""

        if self.node_key and self.source_key:
            return f"{self.node_key}:{self.source_key}"
        if self.node_key:
            return f"{self.node_key}:{self.output_path.as_posix()}"
        return self.output_path.as_posix()


@dataclass(frozen=True)
class EmissionPlan:
    """Planned files before writing to disk."""

    language: str
    template_root: Path
    output_root: Path
    files: Sequence[EmissionFile] = field(default_factory=tuple)


@dataclass(frozen=True)
class EmissionWriteResult:
    """Result of writing planned files."""

    created: Sequence[Path] = field(default_factory=tuple)
    updated: Sequence[Path] = field(default_factory=tuple)
    unchanged: Sequence[Path] = field(default_factory=tuple)
    skipped: Sequence[Path] = field(default_factory=tuple)
    immutable_created: Sequence[Path] = field(default_factory=tuple)
    immutable_skipped: Sequence[Path] = field(default_factory=tuple)
    refused: Sequence[Path] = field(default_factory=tuple)
    refusal_reasons: Mapping[Path, str] = field(default_factory=dict)


@dataclass(frozen=True)
class EmissionResult:
    """Complete result returned by the emission engine."""

    plan: EmissionPlan
    write_result: EmissionWriteResult
