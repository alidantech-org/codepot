"""Template package defaults config contracts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TemplateDefaultsConfig(BaseModel):
    """Default options for a template package."""

    model_config = ConfigDict(frozen=True)

    output: str = "generated"
    global_alias: str = "shared"
    global_folders: tuple[str, ...] = Field(default_factory=tuple)