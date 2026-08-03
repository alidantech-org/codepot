"""Field-set template context contracts."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.contracts.spec.refs import SpecRef
from archives.codepot.src.contracts.templates.context.base import TemplateBaseContext
from archives.codepot.src.contracts.templates.shared.items import (
    TemplateCollectionContext,
    TemplateItemContext,
    TemplateOwnerContext,
)
from archives.codepot.src.spec.ir.schema.field_set.definition import FieldSetDefinition


@dataclass(frozen=True)
class TemplateFieldSetFieldContext:
    """Template context for one field-set field ref."""

    ref: SpecRef


@dataclass(frozen=True)
class TemplateFieldSetContext:
    """Template context for one field set."""

    item: TemplateItemContext[FieldSetDefinition]
    fields: tuple[TemplateFieldSetFieldContext, ...]


@dataclass(frozen=True)
class TemplateFieldSetsEachContext:
    """Context for ``select: field_sets.each``."""

    base: TemplateBaseContext
    field_set: TemplateFieldSetContext
    item: TemplateFieldSetContext
    owner: TemplateOwnerContext | None = None


@dataclass(frozen=True)
class TemplateFieldSetsAllContext:
    """Context for ``select: field_sets.all``."""

    base: TemplateBaseContext
    field_sets: tuple[TemplateFieldSetContext, ...]
    items: TemplateCollectionContext[TemplateFieldSetContext]


@dataclass(frozen=True)
class TemplateFieldSetsByOwnerContext:
    """Context for ``select: field_sets.by_owner``."""

    base: TemplateBaseContext
    owner: TemplateOwnerContext
    field_sets: tuple[TemplateFieldSetContext, ...]
    items: TemplateCollectionContext[TemplateFieldSetContext]
