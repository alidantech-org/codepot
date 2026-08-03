"""Pipeline result/report contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from archives.codepot.src.pipeline.contracts.diagnostics import PipelineDiagnostic


class PassStatus(StrEnum):
    """Status for one pipeline pass."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class ReportCounter:
    """One named report counter."""

    name: str
    value: int
    label: str | None = None


@dataclass(frozen=True)
class PassReport:
    """Report emitted by one pipeline pass."""

    name: str
    title: str
    status: PassStatus
    message: str
    started_at: datetime
    finished_at: datetime
    duration_ms: int
    counters: tuple[ReportCounter, ...] = ()
    diagnostics: tuple[PipelineDiagnostic, ...] = ()
    debug: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class PipelineReport:
    """Complete pipeline execution report."""

    status: PassStatus
    reports: tuple[PassReport, ...]
    diagnostics: tuple[PipelineDiagnostic, ...]
