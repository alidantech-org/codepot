"""Route template context contracts."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.contracts.language.context import LanguageRoute
from archives.codepot.src.contracts.spec.refs import SpecRef
from archives.codepot.src.contracts.templates.context.base import TemplateBaseContext
from archives.codepot.src.contracts.templates.context.route_path import TemplateRoutePathContext
from archives.codepot.src.contracts.templates.shared.flags import TemplateRouteFlags
from archives.codepot.src.contracts.templates.shared.items import (
    TemplateCollectionContext,
    TemplateItemContext,
    TemplateResourceLiteContext,
)
from archives.codepot.src.spec.ir.resource.route.definition import RouteMethodDefinition


@dataclass(frozen=True)
class TemplateRouteBodyContext:
    """Template context for route request body."""

    schema: SpecRef
    content_type: SpecRef
    content_types: tuple[SpecRef, ...]


@dataclass(frozen=True)
class TemplateRouteResponseContext:
    """Template context for one route response."""

    status: int | None
    schema: SpecRef | None = None
    content_type: SpecRef | None = None
    content_types: tuple[SpecRef, ...] = ()
    error_response: SpecRef | None = None
    headers: tuple[tuple[str, SpecRef], ...] = ()


@dataclass(frozen=True)
class TemplateRouteContext:
    """Template context for one method-level route binding."""

    item: TemplateItemContext[RouteMethodDefinition]
    resource: TemplateResourceLiteContext
    route_path: TemplateRoutePathContext | None

    method: str
    operation: SpecRef

    security: SpecRef | object | None = None
    params: SpecRef | None = None
    query: SpecRef | None = None
    body: TemplateRouteBodyContext | None = None
    responses: tuple[TemplateRouteResponseContext, ...] = ()

    flags: TemplateRouteFlags = TemplateRouteFlags()
    lang: LanguageRoute | None = None


@dataclass(frozen=True)
class TemplateRoutesEachContext:
    """Context for ``select: routes.each``."""

    base: TemplateBaseContext
    route: TemplateRouteContext
    item: TemplateRouteContext
    route_path: TemplateRoutePathContext | None
    resource: TemplateResourceLiteContext


@dataclass(frozen=True)
class TemplateRoutesAllContext:
    """Context for ``select: routes.all``."""

    base: TemplateBaseContext
    routes: tuple[TemplateRouteContext, ...]
    items: TemplateCollectionContext[TemplateRouteContext]


@dataclass(frozen=True)
class TemplateRoutesByResourceContext:
    """Context for ``select: routes.by_resource``."""

    base: TemplateBaseContext
    resource: TemplateResourceLiteContext
    routes: tuple[TemplateRouteContext, ...]
    route_paths: tuple[TemplateRoutePathContext, ...]
    items: TemplateCollectionContext[TemplateRouteContext]
