"""Shared pytest fixtures for generator tests."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def project_root() -> Path:
    """Return the Python package repository root used by tests."""
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def bundled_templates_root(project_root: Path) -> Path:
    """Return the template root that is packaged inside the CodepotG wheel."""
    return project_root / "src" / "codepotg" / "templates"


@pytest.fixture
def sample_openapi_path(project_root: Path) -> Path:
    """Return the committed OpenAPI fixture path."""
    return project_root / "tests" / "fixtures" / "sample_openapi.yaml"


@pytest.fixture
def temp_output_path(tmp_path: Path) -> Path:
    """Return a temporary output directory."""
    return tmp_path / "output"


@pytest.fixture
def temp_templates_path(tmp_path: Path) -> Path:
    """Return a temporary templates directory."""
    return tmp_path / "templates"
