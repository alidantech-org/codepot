"""Pipeline report presentation."""

from __future__ import annotations

from archives.codepot.src.cli.presentation.console import console
from archives.codepot.src.pipeline.contracts.diagnostics import PipelineDiagnosticLevel
from archives.codepot.src.pipeline.contracts.events import PipelineEvent
from archives.codepot.src.pipeline.contracts.results import PassReport, PassStatus, PipelineReport


def print_pipeline_event(event: PipelineEvent) -> None:
    """Print one live pipeline event."""

    console.print(f"[dim]{event.pass_name}[/dim] {event.message}")


def _status_icon(status: PassStatus) -> str:
    """Return display icon for pass status."""

    if status == PassStatus.SUCCESS:
        return "[green]OK[/green]"
    if status == PassStatus.WARNING:
        return "[yellow]![/yellow]"
    if status == PassStatus.FAILED:
        return "[red]X[/red]"
    if status == PassStatus.SKIPPED:
        return "[dim]-[/dim]"

    return "[dim]•[/dim]"


def _counter_text(report: PassReport) -> str:
    """Return compact counter text."""

    if not report.counters:
        return ""

    parts = tuple(
        f"{counter.name}={counter.label or counter.value}"
        for counter in report.counters
    )
    return " [dim](" + ", ".join(parts) + ")[/dim]"


def print_pass_report(report: PassReport) -> None:
    """Print one pass report."""

    console.print(
        f"{_status_icon(report.status)} {report.title}: "
        f"{report.message}{_counter_text(report)}"
    )

    for diagnostic in report.diagnostics:
        style = "red" if diagnostic.level == PipelineDiagnosticLevel.ERROR else "yellow"
        console.print(f"  [{style}]{diagnostic.level}:[/{style}] {diagnostic.message}")


def print_pipeline_report(report: PipelineReport) -> None:
    """Print a full pipeline report."""

    for pass_report in report.reports:
        print_pass_report(pass_report)

    if report.status == PassStatus.FAILED:
        console.print("[red]Pipeline failed.[/red]")
    elif report.status == PassStatus.WARNING:
        console.print("[yellow]Pipeline completed with warnings.[/yellow]")
    else:
        console.print("[green]Pipeline completed successfully.[/green]")
