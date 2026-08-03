"""Template package settings config contracts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TemplateSettingsConfig(BaseModel):
    """Validation and authoring settings for a template package."""

    model_config = ConfigDict(frozen=True)

    require_template_select: bool = True
    validate_unique_outputs: bool = True
    validate_resolves: bool = True
    validate_template_files: bool = True
    validate_output_variables: bool = True
