from __future__ import annotations

import tomllib
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[2]
CORE_ROOT = PACKAGE_ROOT.parent / "dryv"


def test_cli_distribution_owns_the_dryv_console_script() -> None:
    cli_project = tomllib.loads((PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    core_project = tomllib.loads((CORE_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert cli_project["project"]["scripts"] == {"dryv": "dryv_cli.main:main"}
    assert "scripts" not in core_project["project"]


def test_cli_distribution_declares_terminal_dependencies_explicitly() -> None:
    project = tomllib.loads((PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = tuple(project["project"]["dependencies"])

    assert any(value.startswith("dryv>=") for value in dependencies)
    assert any(value.startswith("click>=") for value in dependencies)
    assert any(value.startswith("rich>=") for value in dependencies)
    assert any(value.startswith("questionary>=") for value in dependencies)
