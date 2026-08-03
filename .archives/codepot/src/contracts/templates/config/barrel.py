"""Template barrel config contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TemplateBarrelExportStrategy(StrEnum):
    """Supported barrel export strategies."""

    NAMED = "named"
    STAR = "star"


class TemplateBarrelConfig(BaseModel):
    """Optional barrel behavior for a template entry.

    The barrel template file is discovered from the same filesystem zone as the
    configured template key. Config controls behavior only, not template paths
    or output filenames.
    """

    model_config = ConfigDict(frozen=True)

    enabled: bool = True
    export: TemplateBarrelExportStrategy = TemplateBarrelExportStrategy.NAMED
    folders: tuple[str, ...] = Field(default_factory=tuple)