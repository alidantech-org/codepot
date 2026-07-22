"""Template package config finder."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from archives.codepot.src.pipeline.templates.constants import CODEPOTX_CONFIG_FILES


@dataclass(frozen=True)
class TemplateConfigLocation:
    """Resolved template package config location."""

    package_path: Path
    config_path: Path


def find_template_config(path: Path) -> TemplateConfigLocation:
    """Find a codepotx template package config file."""

    if path.is_file():
        return TemplateConfigLocation(
            package_path=path.parent,
            config_path=path,
        )

    for filename in CODEPOTX_CONFIG_FILES:
        candidate = path / filename
        if candidate.is_file():
            return TemplateConfigLocation(
                package_path=path,
                config_path=candidate,
            )

    expected = ", ".join(CODEPOTX_CONFIG_FILES)
    raise FileNotFoundError(
        f"Could not find template config in {path}. Expected: {expected}"
    )
