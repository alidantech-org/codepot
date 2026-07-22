"""Composite template context contracts."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.contracts.language.context import LanguageField
from archives.codepot.src.contracts.spec.refs import SpecRef
from archives.codepot.src.contracts.templates.context.base import TemplateBaseContext
from archives.codepot.src.contracts.templates.shared.flags import TemplateFieldFlags, TemplateSchemaFlags
from archives.codepot.src.contracts.templates.shared.items import (
    TemplateCollectionContext,
    TemplateFieldContext,
    TemplateItemContext,
    TemplateOwnerContext,
)
from archives.codepot.src.spec.ir.properties.composite.definition import CompositeDefinition


@dataclass(frozen=True)
class TemplateCompositeFieldContext:
    """Template context for one composite field."""

    field: TemplateFieldContext[object]
    source_ref: SpecRef | None = None
    source: object | None = None

    type: str | None = None
    format: str | None = None
    validation: object | None = None

    flags: TemplateFieldFlags = TemplateFieldFlags()
    lang: LanguageField | None = None


@dataclass(frozen=True)
class TemplateCompositeContext:
    """Template context for one composite."""

    item: TemplateItemContext[CompositeDefinition]
    fields: tuple[TemplateCompositeFieldContext, ...]
    flags: TemplateSchemaFlags
    extends: SpecRef | None = None
    resource: SpecRef | None = None
    entity: SpecRef | None = None


@dataclass(frozen=True)
class TemplateCompositesEachContext:
    """Context for ``select: composites.each``."""

    base: TemplateBaseContext
    composite: TemplateCompositeContext
    item: TemplateCompositeContext
    owner: TemplateOwnerContext | None = None


@dataclass(frozen=True)
class TemplateCompositesAllContext:
    """Context for ``select: composites.all``."""

    base: TemplateBaseContext
    composites: tuple[TemplateCompositeContext, ...]
    items: TemplateCollectionContext[TemplateCompositeContext]


@dataclass(frozen=True)
class TemplateCompositesByOwnerContext:
    """Context for ``select: composites.by_owner``."""

    base: TemplateBaseContext
    owner: TemplateOwnerContext
    composites: tuple[TemplateCompositeContext, ...]
    items: TemplateCollectionContext[TemplateCompositeContext]
