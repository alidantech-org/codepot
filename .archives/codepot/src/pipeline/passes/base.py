"""Base pipeline pass contracts and report helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Protocol

from archives.codepot.src.pipeline.contracts.diagnostics import PipelineDiagnostic
from archives.codepot.src.pipeline.contracts.results import PassReport, PassStatus, ReportCounter

if TYPE_CHECKING:
    from archives.codepot.src.pipeline.contracts.state import PipelineState


@dataclass(frozen=True)
class PassResult:
    """Result returned by one pipeline pass."""

    state: PipelineState
    report: PassReport


class PipelinePass(Protocol):
    """Protocol implemented by every pipeline pass."""

    name: str
    title: str

    def run(self, state: PipelineState) -> PassResult: # type: ignore
        """Run this pass and return the updated state/report."""


def utc_now() -> datetime:
    """Return the current UTC timestamp."""

    return datetime.now(UTC)


def duration_ms(started_at: datetime, finished_at: datetime) -> int:
    """Return duration in milliseconds."""

    return int((finished_at - started_at).total_seconds() * 1000)


def make_report(
    *,
    name: str,
    title: str,
    status: PassStatus,
    message: str,
    started_at: datetime,
    counters: tuple[ReportCounter, ...] = (),
    diagnostics: tuple[PipelineDiagnostic, ...] = (),
    debug: tuple[tuple[str, str], ...] = (),
) -> PassReport:
    """Create a complete pass report."""

    finished_at = utc_now()

    return PassReport(
        name=name,
        title=title,
        status=status,
        message=message,
        started_at=started_at,
        finished_at=finished_at,
        duration_ms=duration_ms(started_at, finished_at),
        counters=counters,
        diagnostics=diagnostics,
        debug=debug,
    )


def success_result(
    *,
    state: PipelineState,
    name: str,
    title: str,
    message: str,
    started_at: datetime,
    counters: tuple[ReportCounter, ...] = (),
    debug: tuple[tuple[str, str], ...] = (),
) -> PassResult:
    """Create a successful pass result."""

    return PassResult(
        state=state,
        report=make_report(
            name=name,
            title=title,
            status=PassStatus.SUCCESS,
            message=message,
            started_at=started_at,
            counters=counters,
            debug=debug,
        ),
    )


def skipped_result(
    *,
    state: PipelineState,
    name: str,
    title: str,
    message: str,
    started_at: datetime,
) -> PassResult:
    """Create a skipped pass result."""

    return PassResult(
        state=state,
        report=make_report(
            name=name,
            title=title,
            status=PassStatus.SKIPPED,
            message=message,
            started_at=started_at,
        ),
    )


def failed_result(
    *,
    state: PipelineState,
    name: str,
    title: str,
    message: str,
    started_at: datetime,
    diagnostic: PipelineDiagnostic,
) -> PassResult:
    """Create a failed pass result with one diagnostic."""

    return PassResult(
        state=state,
        report=make_report(
            name=name,
            title=title,
            status=PassStatus.FAILED,
            message=message,
            started_at=started_at,
            diagnostics=(diagnostic,),
        ),
    )
