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
def real_openapi_json_path(project_root: Path) -> Path:
    """Return the committed real-world JSON OpenAPI contract."""
    path = project_root / "tests" / "fixtures" / "openapi.json"
    assert path.is_file(), f"Missing real OpenAPI JSON fixture: {path}"
    return path


@pytest.fixture
def real_openapi_yaml_path(project_root: Path) -> Path:
    """Return the committed real-world YAML OpenAPI contract."""
    path = project_root / "tests" / "fixtures" / "openapi.yaml"
    assert path.is_file(), f"Missing real OpenAPI YAML fixture: {path}"
    return path


@pytest.fixture(params=("json", "yaml"), ids=("real-json", "real-yaml"))
def real_openapi_path(
    request: pytest.FixtureRequest,
    real_openapi_json_path: Path,
    real_openapi_yaml_path: Path,
) -> Path:
    """Run format-neutral contract tests against both real fixture formats."""
    return (
        real_openapi_json_path
        if request.param == "json"
        else real_openapi_yaml_path
    )


@pytest.fixture
def temp_output_path(tmp_path: Path) -> Path:
    """Return a temporary output directory."""
    return tmp_path / "output"


@pytest.fixture
def temp_templates_path(tmp_path: Path) -> Path:
    """Return a temporary templates directory."""
    return tmp_path / "templates"
