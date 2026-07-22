"""Template config variable contracts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TemplateOutputVariableConfig(BaseModel):
    """Documented output path variable available for config paths."""

    model_config = ConfigDict(frozen=True)

    path: str
    description: str
    select_modes: tuple[str, ...] = ()
    example: str | None = None


class TemplateConfigVariableCatalog(BaseModel):
    """Configured or generated catalog of output path variables."""

    model_config = ConfigDict(frozen=True)

    variables: tuple[TemplateOutputVariableConfig, ...]
