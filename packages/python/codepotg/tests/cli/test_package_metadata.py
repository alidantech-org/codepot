from __future__ import annotations

import tomllib
from pathlib import Path


def test_package_metadata_exposes_only_codepotg_console_script() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text())

    assert pyproject["project"]["name"] == "codepotg"
    assert pyproject["project"]["scripts"] == {"codepotg": "codepotg.cli.main:app"}
