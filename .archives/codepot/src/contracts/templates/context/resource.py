"""Resource template context contracts."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.contracts.spec.refs import SpecRef
from archives.codepot.src.contracts.templates.context.base import TemplateBaseContext
from archives.codepot.src.contracts.templates.context.operation import TemplateOperationContext
from archives.codepot.src.contracts.templates.context.route import TemplateRouteContext
from archives.codepot.src.contracts.templates.context.route_path import TemplateRoutePathContext
from archives.codepot.src.contracts.templates.shared.flags import TemplateResourceFlags
from archives.codepot.src.contracts.templates.shared.items import (
    TemplateCollectionContext,
    TemplateItemContext,
    TemplateResourceLiteContext,
)
from archives.codepot.src.spec.ir.resource.definition import ResourceDefinition


@dataclass(frozen=True)
class TemplateResourceDefaultsContext:
    """Template context for resource defaults."""

    security: SpecRef | None = None


@dataclass(frozen=True)
class TemplateResourceContext:
    """Template context for one resource."""

    item: TemplateItemContext[ResourceDefinition]
    resource: TemplateResourceLiteContext

    base_path: str
    folders: tuple[str, ...]
    defaults: TemplateResourceDefaultsContext

    operations: tuple[TemplateOperationContext, ...]
    route_paths: tuple[TemplateRoutePathContext, ...]
    routes: tuple[TemplateRouteContext, ...]

    flags: TemplateResourceFlags


@dataclass(frozen=True)
class TemplateResourcesEachContext:
    """Context for ``select: resources.each``."""

    base: TemplateBaseContext
    resource: TemplateResourceContext
    item: TemplateResourceContext


@dataclass(frozen=True)
class TemplateResourcesAllContext:
    """Context for ``select: resources.all``."""

    base: TemplateBaseContext
    resources: tuple[TemplateResourceContext, ...]
    items: TemplateCollectionContext[TemplateResourceContext]
