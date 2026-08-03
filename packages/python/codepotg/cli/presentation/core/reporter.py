"""Small progress reporter for long-running CLI workflows."""

from __future__ import annotations

from archives.codepotg.cli.presentation.core.console import console, error_console

from app.models import RuntimeEvent


class Reporter:
    """Render runtime progress events with optional verbose details."""

    def __init__(self, *, verbose: bool = False) -> None:
        self.verbose = verbose
        self._seen_messages: set[tuple[str, str]] = set()

    def event(self, event: RuntimeEvent) -> None:
        """Render a runtime event."""
        if event.stage in {"command_stdout", "command_stderr"}:
            return

        if event.stage in {
            "rendering_file",
            "file_created",
            "file_updated",
            "file_unchanged",
            "file_skipped",
            "file_immutable_skipped",
            "dependencies_resolved",
            "loading_path_config",
            "scanning_templates",
            "emission_plan_created",
            "emission_dry_run",
            "language_post_actions",
            "resolving_language",
        }:
            self.detail(event.message)
            return

        if event.stage == "command_start":
            self.step(event.message)
            self._command_details(event)
            return

        if event.stage == "command_dry_run":
            self.step(event.message)
            self._command_details(event)
            return

        if event.level == "warning":
            self.warning(event.message)
            self._command_details(event)
            return

        if event.level == "error":
            self.error(event.message)
            self._command_details(event)
            return

        self.step(event.message)

    def section(self, title: str) -> None:
        console.rule(f"[bold #7F77DD]{title}[/bold #7F77DD]", style="bright_black")

    def step(self, message: str) -> None:
        if not self._mark_seen("step", message):
            return
        console.print(f"[#378ADD]->[/#378ADD] {message}")

    def info(self, message: str) -> None:
        console.print(f"[#378ADD]i[/#378ADD] [dim]{message}[/dim]")

    def success(self, message: str) -> None:
        console.print(f"[#1D9E75]+[/#1D9E75] {message}")

    def warning(self, message: str) -> None:
        console.print(f"[#EF9F27]! warning:[/#EF9F27] {message}")

    def error(self, message: str) -> None:
        error_console.print(f"[#E24B4A]x[/#E24B4A] {message}")

    def detail(self, message: str) -> None:
        if self.verbose:
            console.print(f"  [dim]{message}[/dim]")

    def _command_details(self, event: RuntimeEvent) -> None:
        cwd = event.details.get("cwd")
        cmd = event.details.get("cmd")
        returncode = event.details.get("returncode")
        if cwd:
            self.detail(f"cwd: {cwd}")
        if cmd:
            self.detail(f"cmd: {cmd}")
        if returncode is not None:
            self.detail(f"exit code: {returncode}")

    def _mark_seen(self, kind: str, message: str) -> bool:
        key = (kind, message)
        if key in self._seen_messages:
            return False
        self._seen_messages.add(key)
        return True
