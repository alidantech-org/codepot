"""Language runtime contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from archives.codepot.src.contracts.spec.names import SpecNameCase


class LanguageImportStrategy(StrEnum):
    """Supported import path strategies."""

    RELATIVE = "relative"
    ALIAS = "alias"
    PACKAGE = "package"
    ROOT = "root"


class LanguageNameRole(StrEnum):
    """Configurable language naming roles."""

    CLASS = "class"
    INTERFACE = "interface"
    ENUM = "enum"
    ENUM_VALUE = "enum_value"
    FIELD = "field"
    METHOD = "method"
    FUNCTION = "function"
    CONSTANT = "constant"
    VARIABLE = "variable"
    FILE = "file"
    FOLDER = "folder"
    MODULE = "module"
    PACKAGE = "package"


@dataclass(frozen=True)
class LanguageNamingRules:
    """Resolved naming rule choices for a language runtime."""

    class_case: SpecNameCase
    interface_case: SpecNameCase
    enum_case: SpecNameCase
    enum_value_case: SpecNameCase
    field_case: SpecNameCase
    method_case: SpecNameCase
    function_case: SpecNameCase
    constant_case: SpecNameCase
    variable_case: SpecNameCase
    file_case: SpecNameCase
    folder_case: SpecNameCase
    module_case: SpecNameCase
    package_case: SpecNameCase


@dataclass(frozen=True)
class LanguageImportRules:
    """Resolved import strategy options for a language runtime."""

    strategy: LanguageImportStrategy
    root: str | None = None
    alias: str | None = None
    package: str | None = None
    include_extension: bool = False
    type_only: bool = False


@dataclass(frozen=True)
class LanguageRuntime:
    """Global language context available as ``language`` in templates."""

    name: str
    extensions: tuple[str, ...]
    package_name: str | None
    package_manager: str | None
    source_root: Path
    naming: LanguageNamingRules
    imports: LanguageImportRules

    @property
    def extension(self) -> str:
        """Return the primary language extension."""

        return self.extensions[0] if self.extensions else ""