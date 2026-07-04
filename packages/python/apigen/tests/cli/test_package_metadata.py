from __future__ import annotations

import tomllib
from pathlib import Path


def test_package_metadata_exposes_only_codepotx_console_script() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text())

    assert pyproject["project"]["name"] == "codepotx"
    assert pyproject["project"]["scripts"] == {"codepotx": "cli.main:app"}
