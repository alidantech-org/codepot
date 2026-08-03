"""Per-item language enrichment contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from archives.codepot.src.contracts.language.names import LanguageName
from archives.codepot.src.contracts.language.types import LanguageType


@dataclass(frozen=True)
class LanguageItem:
    """Generic ``.lang`` context for a spec/template item.

    This is intentionally generic so every spec item can expose one ``.lang``
    object without creating a language contract file per item type.
    """

    name: LanguageName
    type: LanguageType | None = None
    annotation: str | None = None

    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class LanguageField:
    """``.lang`` context for a field-like template item."""

    name: LanguageName
    type: LanguageType
    annotation: str

    is_optional: bool
    is_nullable: bool
    is_array: bool

    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class LanguageOperation:
    """``.lang`` context for operation-like items."""

    name: LanguageName
    input_type: LanguageType | None = None
    output_type: LanguageType | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class LanguageRoute:
    """``.lang`` context for route and route-path items."""

    name: LanguageName
    method_name: str | None = None
    path_constant_name: str | None = None
    metadata: dict[str, Any] | None = None
