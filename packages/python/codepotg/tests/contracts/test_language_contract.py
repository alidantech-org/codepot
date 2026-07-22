"""Tests for language adapter contract expectations."""

from __future__ import annotations

from src.contracts.language import LanguagePostResult


def test_language_post_result_defaults_empty() -> None:
    result = LanguagePostResult()

    assert result.actions == ()
    assert result.diagnostics == ()
