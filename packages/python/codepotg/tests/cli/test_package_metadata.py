from __future__ import annotations

import re
import tomllib
from pathlib import Path

EXPECTED_VERSION = "1.0.0"


def test_package_metadata_exposes_only_codepotg_console_script() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["name"] == "codepotg"
    assert pyproject["project"]["scripts"] == {"codepotg": "codepotg.cli.main:app"}


def test_release_version_is_consistent() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    package_source = Path("src/codepotg/__init__.py").read_text(encoding="utf-8")
    cli_constants = Path("cli/constants/constants.py").read_text(encoding="utf-8")

    package_match = re.search(
        r'^__version__\s*=\s*["\']([^"\']+)["\']',
        package_source,
        re.MULTILINE,
    )
    cli_match = re.search(
        r'^APP_VERSION\s*=\s*["\']([^"\']+)["\']',
        cli_constants,
        re.MULTILINE,
    )

    assert pyproject["project"]["version"] == EXPECTED_VERSION
    assert package_match is not None and package_match.group(1) == EXPECTED_VERSION
    assert cli_match is not None and cli_match.group(1) == EXPECTED_VERSION


def test_release_metadata_is_pypi_ready() -> None:
    pyproject_text = Path("pyproject.toml").read_text(encoding="utf-8")
    project = tomllib.loads(pyproject_text)["project"]

    assert project["description"]
    assert project["readme"]["file"] == "README.md"
    assert project["license"] == "MIT"
    assert project["license-files"] == ["LICENSE"]
    assert project["requires-python"] == ">=3.11"
    assert project["urls"]["Repository"].startswith("https://github.com/")
    assert Path("README.md").is_file()
    assert Path("RELEASE.md").is_file()
    assert Path("LICENSE").is_file()
    assert Path("MANIFEST.in").is_file()
