"""Route path template context contracts."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.contracts.language.context import LanguageRoute
from archives.codepot.src.contracts.spec.refs import SpecRef
from archives.codepot.src.contracts.templates.context.base import TemplateBaseContext
from archives.codepot.src.contracts.templates.shared.items import (
    TemplateCollectionContext,
    TemplateItemContext,
    TemplateResourceLiteContext,
)
from archives.codepot.src.spec.ir.resource.route.definition import RoutePathDefinition


@dataclass(frozen=True)
class TemplateRoutePathParameterContext:
    """Template context for one path-level parameter."""

    key: str
    ref: SpecRef


@dataclass(frozen=True)
class TemplateRoutePathContext:
    """Template context for one route path."""

    item: TemplateItemContext[RoutePathDefinition]
    resource: TemplateResourceLiteContext

    path: str
    parameters: tuple[TemplateRoutePathParameterContext, ...]
    params: tuple[TemplateRoutePathParameterContext, ...]

    method_names: tuple[str, ...]
    methods: tuple[object, ...]

    operations: tuple[SpecRef, ...] = ()
    lang: LanguageRoute | None = None


@dataclass(frozen=True)
class TemplateRoutePathsEachContext:
    """Context for ``select: route_paths.each``."""

    base: TemplateBaseContext
    route_path: TemplateRoutePathContext
    item: TemplateRoutePathContext
    resource: TemplateResourceLiteContext


@dataclass(frozen=True)
class TemplateRoutePathsAllContext:
    """Context for ``select: route_paths.all``."""

    base: TemplateBaseContext
    route_paths: tuple[TemplateRoutePathContext, ...]
    items: TemplateCollectionContext[TemplateRoutePathContext]


@dataclass(frozen=True)
class TemplateRoutePathsByResourceContext:
    """Context for ``select: route_paths.by_resource``."""

    base: TemplateBaseContext
    resource: TemplateResourceLiteContext
    route_paths: tuple[TemplateRoutePathContext, ...]
    items: TemplateCollectionContext[TemplateRoutePathContext]
