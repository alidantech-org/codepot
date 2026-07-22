"""Template package config loader."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from archives.codepot.src.contracts.templates.config.package import (
    LoadedTemplatePackageConfig,
    TemplatePackageConfig,
    TemplatePackageFormat,
)
from archives.codepot.src.pipeline.templates.constants import JSON_SUFFIX, YAML_SUFFIX, YML_SUFFIX
from archives.codepot.src.pipeline.templates.finder import find_template_config
from archives.codepot.src.utils.loaders.json_loader import load_json_file
from archives.codepot.src.utils.loaders.yaml_loader import load_yaml_file


def _config_format(path: Path) -> TemplatePackageFormat:
    """Detect template config format from file suffix."""

    suffix = path.suffix.lower()

    if suffix == YAML_SUFFIX:
        return TemplatePackageFormat.YAML
    if suffix == YML_SUFFIX:
        return TemplatePackageFormat.YML
    if suffix == JSON_SUFFIX:
        return TemplatePackageFormat.JSON

    raise ValueError(f"Unsupported template config format: {path}")


def _load_config_data(
    path: Path,
    config_format: TemplatePackageFormat,
) -> dict[str, Any]:
    """Load template config data."""

    if config_format in {TemplatePackageFormat.YAML, TemplatePackageFormat.YML}:
        return load_yaml_file(path)

    if config_format == TemplatePackageFormat.JSON:
        return load_json_file(path)

    raise ValueError(f"Unsupported template config format: {config_format}")


def load_template_package(path: Path) -> LoadedTemplatePackageConfig:
    """Load a codepotx template package config."""

    location = find_template_config(path)
    config_format = _config_format(location.config_path)
    data = _load_config_data(location.config_path, config_format)
    config = TemplatePackageConfig.model_validate(data)

    return LoadedTemplatePackageConfig(
        package_path=location.package_path,
        config_path=location.config_path,
        format=config_format,
        config=config,
    )