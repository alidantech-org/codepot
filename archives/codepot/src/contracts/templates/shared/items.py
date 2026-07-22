"""Reusable template item context contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from archives.codepot.src.contracts.language.context import LanguageField, LanguageItem, LanguageOperation, LanguageRoute
from archives.codepot.src.contracts.spec.records import SpecRecord
from archives.codepot.src.contracts.spec.refs import SpecOwner, SpecRef
from archives.codepot.src.contracts.templates.shared.dependencies import TemplateDependencies
from archives.codepot.src.contracts.templates.shared.flags import (
    TemplateDependencyFlags,
    TemplateFieldFlags,
    TemplateSchemaFlags,
)

TData = TypeVar("TData")


@dataclass(frozen=True)
class TemplateItemContext(Generic[TData]):
    """Generic template item context.

    The item wraps a normalized spec record, the original IR data, optional
    language enrichment, and dependency information.
    """

    record: SpecRecord[TData]
    key: str
    ref: SpecRef
    name: object
    data: TData
    lang: LanguageItem | None = None
    owner: SpecOwner | None = None
    dependencies: TemplateDependencies | None = None
    dependency_flags: TemplateDependencyFlags = TemplateDependencyFlags()


@dataclass(frozen=True)
class TemplateFieldContext(Generic[TData]):
    """Generic field-like template context."""

    record: SpecRecord[TData] | None
    key: str
    ref: SpecRef | None
    name: object
    data: TData
    flags: TemplateFieldFlags
    lang: LanguageField | None = None
    source: object | None = None
    source_ref: SpecRef | None = None


@dataclass(frozen=True)
class TemplateSchemaContext(Generic[TData]):
    """Generic schema-like template context."""

    item: TemplateItemContext[TData]
    fields: tuple[TemplateFieldContext[object], ...]
    flags: TemplateSchemaFlags


@dataclass(frozen=True)
class TemplateOperationItemContext(Generic[TData]):
    """Generic operation-like template context."""

    item: TemplateItemContext[TData]
    lang: LanguageOperation | None = None


@dataclass(frozen=True)
class TemplateRouteItemContext(Generic[TData]):
    """Generic route-like template context."""

    item: TemplateItemContext[TData]
    lang: LanguageRoute | None = None


@dataclass(frozen=True)
class TemplateOwnerContext:
    """Owner bucket context for by_owner selections."""

    key: str
    ref: SpecRef
    name: object
    folders: tuple[str, ...] = ()


@dataclass(frozen=True)
class TemplateResourceLiteContext:
    """Lightweight resource context for grouped output paths and templates."""

    key: str
    ref: SpecRef
    name: object
    base_path: str
    folders: tuple[str, ...]


@dataclass(frozen=True)
class TemplateCollectionContext(Generic[TData]):
    """Generic collection context for all/grouped selections."""

    items: tuple[TData, ...]