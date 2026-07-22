"""Tests for diagnostics formatting."""

from __future__ import annotations

from cli.presentation.core.diagnostics import count_diagnostics


class Diagnostic:
    """Simple diagnostic fixture."""

    def __init__(self, level: str) -> None:
        self.level = level
        self.message = level


def test_count_diagnostics_by_level() -> None:
    counts = count_diagnostics([Diagnostic("info"), Diagnostic("error"), Diagnostic("info")])

    assert counts["info"] == 2
    assert counts["error"] == 1
