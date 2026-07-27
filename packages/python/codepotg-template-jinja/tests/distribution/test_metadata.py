from __future__ import annotations

import tomllib
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def test_distribution_metadata_and_entry_point() -> None:
    data = tomllib.loads((PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = data["project"]
    assert project["name"] == "codepotg-template-jinja"
    assert project["version"] == "2.0.0a1"
    assert project["requires-python"] == ">=3.11"
    assert project["dependencies"] == [
        "codepotg-core>=2.0.0a1,<2.1",
        "Jinja2>=3.1.4,<4.0",
    ]
    assert project["entry-points"]["codepotg.template_engines"]["jinja"] == (
        "codepotg_template_jinja.plugin:create_plugin"
    )


def test_typing_marker_exists() -> None:
    assert (PACKAGE_ROOT / "src" / "codepotg_template_jinja" / "py.typed").is_file()
