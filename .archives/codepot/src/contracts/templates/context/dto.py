"""DTO template context contracts."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.contracts.language.context import LanguageField
from archives.codepot.src.contracts.spec.refs import SpecRef
from archives.codepot.src.contracts.templates.context.base import TemplateBaseContext
from archives.codepot.src.contracts.templates.shared.flags import (
    TemplateFieldFlags,
    TemplateSchemaFlags,
)
from archives.codepot.src.contracts.templates.shared.items import (
    TemplateCollectionContext,
    TemplateFieldContext,
    TemplateItemContext,
    TemplateOwnerContext,
)
from archives.codepot.src.spec.ir.schema.dto.definition import DtoDefinition, DtoFieldDefinition


@dataclass(frozen=True)
class TemplateDtoFieldContext:
    """Template context for one DTO field."""

    field: TemplateFieldContext[DtoFieldDefinition]
    source_ref: SpecRef | None = None
    source: object | None = None

    type: str | None = None
    format: str | None = None
    validation: object | None = None

    flags: TemplateFieldFlags = TemplateFieldFlags()
    lang: LanguageField | None = None


@dataclass(frozen=True)
class TemplateDtoContext:
    """Template context for one DTO."""

    item: TemplateItemContext[DtoDefinition]
    fields: tuple[TemplateDtoFieldContext, ...]
    flags: TemplateSchemaFlags
    extends: SpecRef | None = None
    source: SpecRef | None = None


@dataclass(frozen=True)
class TemplateDtosEachContext:
    """Context for ``select: dtos.each``."""

    base: TemplateBaseContext
    dto: TemplateDtoContext
    item: TemplateDtoContext
    owner: TemplateOwnerContext | None = None


@dataclass(frozen=True)
class TemplateDtosAllContext:
    """Context for ``select: dtos.all``."""

    base: TemplateBaseContext
    dtos: tuple[TemplateDtoContext, ...]
    items: TemplateCollectionContext[TemplateDtoContext]


@dataclass(frozen=True)
class TemplateDtosByOwnerContext:
    """Context for ``select: dtos.by_owner``."""

    base: TemplateBaseContext
    owner: TemplateOwnerContext
    dtos: tuple[TemplateDtoContext, ...]
    items: TemplateCollectionContext[TemplateDtoContext]
