"""Tests for CLI table helpers."""

from __future__ import annotations

from cli.presentation.core.tables import _format_key, _format_value


def test_format_key_preserves_api_acronym() -> None:
    assert _format_key("openapi_version") == "OpenAPI Version"
    assert _format_key("api_version") == "API Version"


def test_format_value_formats_none_as_dash() -> None:
    assert "—" in _format_value(None) or "-" in _format_value(None)
