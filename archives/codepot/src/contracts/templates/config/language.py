"""Template language config contracts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from archives.codepot.src.contracts.spec.names import SpecNameCase


class TemplateLanguageNamingConfig(BaseModel):
    """User-configurable naming cases for a language."""

    model_config = ConfigDict(frozen=True)

    class_name: SpecNameCase = SpecNameCase.PASCAL
    interface: SpecNameCase = SpecNameCase.PASCAL
    enum: SpecNameCase = SpecNameCase.PASCAL
    enum_value: SpecNameCase = SpecNameCase.CONSTANT
    field: SpecNameCase = SpecNameCase.CAMEL
    method: SpecNameCase = SpecNameCase.CAMEL
    function: SpecNameCase = SpecNameCase.CAMEL
    constant: SpecNameCase = SpecNameCase.SCREAMING_SNAKE
    variable: SpecNameCase = SpecNameCase.CAMEL
    file: SpecNameCase = SpecNameCase.PATH
    folder: SpecNameCase = SpecNameCase.PATH
    module: SpecNameCase = SpecNameCase.PATH
    package: SpecNameCase = SpecNameCase.SNAKE


class TemplateLanguageImportConfig(BaseModel):
    """User-configurable import strategy."""

    model_config = ConfigDict(frozen=True)

    strategy: str = "relative"
    root: str | None = None
    alias: str | None = None
    package: str | None = None
    type_only: bool = False
    extension: bool = False


class TemplateLanguageConfig(BaseModel):
    """Language block in ``codepotx`` config."""

    model_config = ConfigDict(frozen=True)

    name: str
    extensions: tuple[str, ...] = Field(default_factory=tuple)
    package_manager: str | None = None
    package_name: str | None = None
    source_root: str = "src"
    naming: TemplateLanguageNamingConfig = Field(
        default_factory=TemplateLanguageNamingConfig
    )
    imports: TemplateLanguageImportConfig = Field(
        default_factory=TemplateLanguageImportConfig
    )

    @property
    def primary_extension(self) -> str | None:
        """Return the first configured language extension."""

        return self.extensions[0] if self.extensions else None