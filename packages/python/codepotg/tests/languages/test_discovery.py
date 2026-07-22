"""Tests for language adapter discovery."""

from __future__ import annotations

from src.languages.discovery import discover_languages, resolve_language_adapter


def test_discover_languages_finds_debug() -> None:
    languages = discover_languages()

    assert "debug" in languages


def test_resolve_language_adapter_by_name() -> None:
    adapter = resolve_language_adapter("debug")

    assert adapter.name == "debug"
    assert adapter.template_name == "debug"


def test_resolve_language_adapter_by_alias() -> None:
    adapter = resolve_language_adapter("txt")

    assert adapter.name == "debug"
