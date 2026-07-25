"""Template entry config contracts."""

from __future__ import annotations

from archives.codepot.src.contracts.templates.config.barrel import TemplateBarrelConfig
from archives.codepot.src.contracts.templates.config.resolve import TemplateResolveMap
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TemplateEntryConfig(BaseModel):
    """One entry under ``templates.<id>`` in codepotx config.

    Template files are discovered from filesystem paths containing a literal
    ``{template_key}`` folder. Config controls selection behavior, dynamic
    folder insertion, barrel behavior, dependency resolution, and custom
    template options.
    """

    model_config = ConfigDict(frozen=True)

    select: str
    folders: tuple[str, ...] = Field(default_factory=tuple)
    barrel: bool | TemplateBarrelConfig = False
    resolves: TemplateResolveMap = Field(default_factory=dict)
    options: dict[str, object] = Field(default_factory=dict)

    @field_validator("folders")
    @classmethod
    def validate_folders(cls, folders: tuple[str, ...]) -> tuple[str, ...]:
        """Ensure folder entries are non-empty strings."""

        for folder in folders:
            if not folder.strip():
                raise ValueError("Template folder entries must not be empty.")

        return folders

    @property
    def barrel_enabled(self) -> bool:
        """Return true when barrel generation is enabled."""

        if isinstance(self.barrel, bool):
            return self.barrel

        return self.barrel.enabled

    @property
    def barrel_export(self) -> str:
        """Return barrel export strategy."""

        if isinstance(self.barrel, bool):
            return "named"

        return self.barrel.export.value

    @property
    def barrel_folders(self) -> tuple[str, ...]:
        """Return extra barrel folders."""

        if isinstance(self.barrel, bool):
            return ()

        return self.barrel.folders