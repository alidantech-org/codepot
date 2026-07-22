"""Tests for CLI path normalization."""

from __future__ import annotations

from cli.paths import normalize_cli_path


def test_normalize_msys_drive_path() -> None:
    assert str(normalize_cli_path("/c/Users/peter/out")) == "C:\\Users\\peter\\out"


def test_normalize_backslash_msys_drive_path() -> None:
    assert str(normalize_cli_path("\\c\\Users\\peter\\out")) == "C:\\Users\\peter\\out"
