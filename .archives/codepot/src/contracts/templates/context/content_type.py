"""Content type template context contracts."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.contracts.templates.context.base import TemplateBaseContext
from archives.codepot.src.contracts.templates.shared.flags import TemplateContentTypeFlags
from archives.codepot.src.contracts.templates.shared.items import (
    TemplateCollectionContext,
    TemplateItemContext,
)
from archives.codepot.src.spec.ir.shared.content import ContentTypeDefinition


@dataclass(frozen=True)
class TemplateContentTypeContext:
    """Template context for one content type."""

    item: TemplateItemContext[ContentTypeDefinition]
    media_type: str
    strategy: str
    binary: bool
    structured: bool
    flags: TemplateContentTypeFlags


@dataclass(frozen=True)
class TemplateContentTypesAllContext:
    """Context for ``select: content_types.all``."""

    base: TemplateBaseContext
    content_types: tuple[TemplateContentTypeContext, ...]
    items: TemplateCollectionContext[TemplateContentTypeContext]


@dataclass(frozen=True)
class TemplateContentTypesEachContext:
    """Context for optional/debug ``select: content_types.each``."""

    base: TemplateBaseContext
    content_type: TemplateContentTypeContext
    item: TemplateContentTypeContext
