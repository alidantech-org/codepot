"""Enum template context contracts."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.contracts.spec.records import SpecRecord
from archives.codepot.src.contracts.templates.context.base import TemplateBaseContext
from archives.codepot.src.contracts.templates.shared.items import (
    TemplateCollectionContext,
    TemplateItemContext,
    TemplateOwnerContext,
)
from archives.codepot.src.spec.ir.properties.enum.definition import (
    EnumDefinition,
    EnumValueDefinition,
)


@dataclass(frozen=True)
class TemplateEnumValueContext:
    """Template context for one enum value."""

    record: SpecRecord[EnumValueDefinition] | None
    key: str
    name: object
    data: EnumValueDefinition
    value: str | int | float
    label: str | None
    lang: object | None = None


@dataclass(frozen=True)
class TemplateEnumContext:
    """Template context for one enum item."""

    item: TemplateItemContext[EnumDefinition]
    values: tuple[TemplateEnumValueContext, ...]


@dataclass(frozen=True)
class TemplateEnumsEachContext:
    """Context for ``select: enums.each``."""

    base: TemplateBaseContext
    enum: TemplateEnumContext
    item: TemplateEnumContext
    owner: TemplateOwnerContext | None = None


@dataclass(frozen=True)
class TemplateEnumsAllContext:
    """Context for ``select: enums.all``."""

    base: TemplateBaseContext
    enums: tuple[TemplateEnumContext, ...]
    items: TemplateCollectionContext[TemplateEnumContext]


@dataclass(frozen=True)
class TemplateEnumsByOwnerContext:
    """Context for ``select: enums.by_owner``."""

    base: TemplateBaseContext
    owner: TemplateOwnerContext
    enums: tuple[TemplateEnumContext, ...]
    items: TemplateCollectionContext[TemplateEnumContext]
