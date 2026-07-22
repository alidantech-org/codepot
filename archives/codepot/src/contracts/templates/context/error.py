"""Error response template context contracts."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.contracts.spec.refs import SpecRef
from archives.codepot.src.contracts.templates.context.base import TemplateBaseContext
from archives.codepot.src.contracts.templates.shared.items import (
    TemplateCollectionContext,
    TemplateItemContext,
    TemplateOwnerContext,
)
from archives.codepot.src.spec.ir.response.errors.definition import ErrorResponseDefinition


@dataclass(frozen=True)
class TemplateErrorHeaderContext:
    """Template context for one error response header."""

    key: str
    ref: SpecRef


@dataclass(frozen=True)
class TemplateErrorContext:
    """Template context for one reusable error response."""

    item: TemplateItemContext[ErrorResponseDefinition]

    status: int
    intent: str | None
    schema: SpecRef
    content_type: SpecRef
    headers: tuple[TemplateErrorHeaderContext, ...]


@dataclass(frozen=True)
class TemplateErrorsEachContext:
    """Context for ``select: errors.each``."""

    base: TemplateBaseContext
    error: TemplateErrorContext
    item: TemplateErrorContext
    owner: TemplateOwnerContext | None = None


@dataclass(frozen=True)
class TemplateErrorsAllContext:
    """Context for ``select: errors.all``."""

    base: TemplateBaseContext
    errors: tuple[TemplateErrorContext, ...]
    items: TemplateCollectionContext[TemplateErrorContext]


@dataclass(frozen=True)
class TemplateErrorsByOwnerContext:
    """Context for ``select: errors.by_owner``."""

    base: TemplateBaseContext
    owner: TemplateOwnerContext
    errors: tuple[TemplateErrorContext, ...]
    items: TemplateCollectionContext[TemplateErrorContext]
