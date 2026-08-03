"""Template output config contracts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TemplateOutputPathConfig(BaseModel):
    """One configured output path.

    ``folders`` is optional. ``file`` is required and may include nested ``/``.
    Final output path is ``folders + file``.
    """

    model_config = ConfigDict(frozen=True)

    file: str
    folders: tuple[str, ...] = ()


class TemplateOutputConfig(BaseModel):
    """Output path config for one template entry."""

    model_config = ConfigDict(frozen=True)

    paths: tuple[TemplateOutputPathConfig, ...] = Field(min_length=1)