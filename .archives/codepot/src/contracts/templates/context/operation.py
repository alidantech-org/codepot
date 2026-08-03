"""Operation template context contracts."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.contracts.language.context import LanguageOperation
from archives.codepot.src.contracts.spec.refs import SpecRef
from archives.codepot.src.contracts.templates.context.base import TemplateBaseContext
from archives.codepot.src.contracts.templates.shared.flags import TemplateOperationFlags
from archives.codepot.src.contracts.templates.shared.items import (
    TemplateCollectionContext,
    TemplateItemContext,
    TemplateResourceLiteContext,
)
from archives.codepot.src.spec.ir.resource.operation.definition import OperationDefinition


@dataclass(frozen=True)
class TemplateOperationInputContext:
    """Template context for operation input."""

    context: tuple[SpecRef, ...]
    params: SpecRef | None = None
    query: SpecRef | None = None
    body: SpecRef | None = None

    params_type: object | None = None
    query_type: object | None = None
    body_type: object | None = None


@dataclass(frozen=True)
class TemplateOperationOutputContext:
    """Template context for operation output."""

    result: SpecRef | None = None
    errors: tuple[SpecRef, ...] = ()

    result_type: object | None = None
    error_types: tuple[object, ...] = ()


@dataclass(frozen=True)
class TemplateOperationContext:
    """Template context for one operation."""

    item: TemplateItemContext[OperationDefinition]
    resource: TemplateResourceLiteContext

    input: TemplateOperationInputContext
    output: TemplateOperationOutputContext

    flags: TemplateOperationFlags
    lang: LanguageOperation | None = None


@dataclass(frozen=True)
class TemplateOperationsEachContext:
    """Context for ``select: operations.each``."""

    base: TemplateBaseContext
    operation: TemplateOperationContext
    item: TemplateOperationContext
    resource: TemplateResourceLiteContext


@dataclass(frozen=True)
class TemplateOperationsAllContext:
    """Context for ``select: operations.all``."""

    base: TemplateBaseContext
    operations: tuple[TemplateOperationContext, ...]
    items: TemplateCollectionContext[TemplateOperationContext]


@dataclass(frozen=True)
class TemplateOperationsByResourceContext:
    """Context for ``select: operations.by_resource``."""

    base: TemplateBaseContext
    resource: TemplateResourceLiteContext
    operations: tuple[TemplateOperationContext, ...]
    items: TemplateCollectionContext[TemplateOperationContext]
