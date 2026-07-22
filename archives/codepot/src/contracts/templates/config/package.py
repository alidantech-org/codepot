"""Template package root config contracts."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from archives.codepot.src.contracts.templates.config.commands import (
    TemplateCommandsConfig,
    TemplateMessagesConfig,
)
from archives.codepot.src.contracts.templates.config.defaults import TemplateDefaultsConfig
from archives.codepot.src.contracts.templates.config.language import TemplateLanguageConfig
from archives.codepot.src.contracts.templates.config.settings import TemplateSettingsConfig
from archives.codepot.src.contracts.templates.config.template import TemplateEntryConfig


class TemplatePackageFormat(StrEnum):
    """Supported template package config formats."""

    YAML = "yaml"
    YML = "yml"
    JSON = "json"


class TemplatePackageConfig(BaseModel):
    """Root model for codepotx template package config."""

    model_config = ConfigDict(frozen=True)

    version: int = 1
    name: str
    label: str | None = None
    description: str | None = None

    language: TemplateLanguageConfig
    defaults: TemplateDefaultsConfig = Field(default_factory=TemplateDefaultsConfig)
    settings: TemplateSettingsConfig = Field(default_factory=TemplateSettingsConfig)

    commands: TemplateCommandsConfig = Field(default_factory=TemplateCommandsConfig)
    messages: TemplateMessagesConfig = Field(default_factory=TemplateMessagesConfig)

    ignore: dict[str, object] = Field(default_factory=dict)
    templates: dict[str, TemplateEntryConfig] = Field(default_factory=dict)


class LoadedTemplatePackageConfig(BaseModel):
    """Loaded template package config with source metadata."""

    model_config = ConfigDict(frozen=True)

    package_path: Path
    config_path: Path
    format: TemplatePackageFormat
    config: TemplatePackageConfig