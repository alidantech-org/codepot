"""Shared pytest fixtures for generator tests."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def project_root() -> Path:
    """Return the repository root used by tests."""
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def sample_openapi_path(project_root: Path) -> Path:
    """Return the sample OpenAPI document path."""
    return project_root / "openapi.yaml"


@pytest.fixture
def temp_output_path(tmp_path: Path) -> Path:
    """Return a temporary output directory."""
    return tmp_path / "output"


@pytest.fixture
def temp_templates_path(tmp_path: Path) -> Path:
    """Return a temporary templates directory."""
    return tmp_path / "templates"
