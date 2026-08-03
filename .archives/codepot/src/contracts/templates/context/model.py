"""Model template context contracts."""

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
from archives.codepot.src.spec.ir.schema.model.definition import (
    ModelDefinition,
    ModelFieldDefinition,
)


@dataclass(frozen=True)
class TemplateModelFieldContext:
    """Template context for one model field."""

    field: TemplateFieldContext[ModelFieldDefinition]
    source_ref: SpecRef | None = None
    source: object | None = None

    type: str | None = None
    format: str | None = None
    validation: object | None = None

    flags: TemplateFieldFlags = TemplateFieldFlags()
    lang: LanguageField | None = None


@dataclass(frozen=True)
class TemplateModelContext:
    """Template context for one model."""

    item: TemplateItemContext[ModelDefinition]
    fields: tuple[TemplateModelFieldContext, ...]
    flags: TemplateSchemaFlags
    extends: SpecRef | None = None
    source: SpecRef | None = None


@dataclass(frozen=True)
class TemplateModelsEachContext:
    """Context for ``select: models.each``."""

    base: TemplateBaseContext
    model: TemplateModelContext
    item: TemplateModelContext
    owner: TemplateOwnerContext | None = None


@dataclass(frozen=True)
class TemplateModelsAllContext:
    """Context for ``select: models.all``."""

    base: TemplateBaseContext
    models: tuple[TemplateModelContext, ...]
    items: TemplateCollectionContext[TemplateModelContext]


@dataclass(frozen=True)
class TemplateModelsByOwnerContext:
    """Context for ``select: models.by_owner``."""

    base: TemplateBaseContext
    owner: TemplateOwnerContext
    models: tuple[TemplateModelContext, ...]
    items: TemplateCollectionContext[TemplateModelContext]
