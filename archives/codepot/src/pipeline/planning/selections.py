"""Template selection planning models and helpers."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.contracts.spec.records import SpecRecord
from archives.codepot.src.contracts.templates.config.selection import (
    TemplateSelect,
    TemplateSelectMode,
    TemplateSelectSubject,
)
from archives.codepot.src.contracts.templates.config.template import TemplateEntryConfig
from archives.codepot.src.pipeline.templates.selection import parse_template_select
from archives.codepot.src.spec.repository.repository import SpecRepository
from archives.codepot.src.spec.utils.enums import SpecSubject


@dataclass(frozen=True)
class PlannedSelectionBucket:
    """One grouped selection bucket."""

    key: str
    records: tuple[SpecRecord[object], ...]


@dataclass(frozen=True)
class PlannedSelection:
    """Planned records for one template entry."""

    template_id: str
    template: TemplateEntryConfig
    select: TemplateSelect
    records: tuple[SpecRecord[object], ...]
    buckets: tuple[PlannedSelectionBucket, ...] = ()


def subject_for_template_subject(subject: TemplateSelectSubject) -> SpecSubject:
    """Map template select subject to repository subject."""

    if subject == TemplateSelectSubject.CONTENT_TYPES:
        return SpecSubject.CONTENT_TYPES

    if subject == TemplateSelectSubject.ENUMS:
        return SpecSubject.ENUMS
    if subject == TemplateSelectSubject.COMPOSITES:
        return SpecSubject.COMPOSITES

    if subject == TemplateSelectSubject.ENTITIES:
        return SpecSubject.ENTITIES
    if subject == TemplateSelectSubject.FIELD_SETS:
        return SpecSubject.FIELD_SETS
    if subject == TemplateSelectSubject.MODELS:
        return SpecSubject.MODELS
    if subject == TemplateSelectSubject.DTOS:
        return SpecSubject.DTOS

    if subject == TemplateSelectSubject.RESOURCES:
        return SpecSubject.RESOURCES
    if subject == TemplateSelectSubject.OPERATIONS:
        return SpecSubject.OPERATIONS
    if subject == TemplateSelectSubject.ROUTE_PATHS:
        return SpecSubject.ROUTE_PATHS
    if subject == TemplateSelectSubject.ROUTES:
        return SpecSubject.ROUTES

    if subject == TemplateSelectSubject.ERRORS:
        return SpecSubject.ERRORS

    if subject == TemplateSelectSubject.SECURITY_CREDENTIALS:
        return SpecSubject.SECURITY_CREDENTIALS
    if subject == TemplateSelectSubject.SECURITY_PRINCIPALS:
        return SpecSubject.SECURITY_PRINCIPALS
    if subject == TemplateSelectSubject.SECURITY_POLICIES:
        return SpecSubject.SECURITY_POLICIES

    raise ValueError(f"Unsupported template select subject: {subject}")


def selected_records(
    *,
    repository: SpecRepository,
    select: TemplateSelect,
) -> tuple[SpecRecord[object], ...]:
    """Return selected records for a parsed template selection."""

    if select.mode == TemplateSelectMode.ONCE:
        return ()

    if select.subject is None:
        raise ValueError(f"Selection requires a subject: {select.raw}")

    subject = subject_for_template_subject(select.subject)
    return repository.records_for(subject)


def owner_buckets(
    records: tuple[SpecRecord[object], ...],
) -> tuple[PlannedSelectionBucket, ...]:
    """Group records by normalized owner key."""

    grouped: dict[str, list[SpecRecord[object]]] = {}

    for record in records:
        owner_key = record.owner.key
        grouped.setdefault(owner_key, []).append(record)

    return tuple(
        PlannedSelectionBucket(key=key, records=tuple(items))
        for key, items in sorted(grouped.items(), key=lambda item: item[0])
    )


def plan_template_selection(
    *,
    template_id: str,
    template: TemplateEntryConfig,
    repository: SpecRepository,
) -> PlannedSelection:
    """Plan selected records for one template entry."""

    select = parse_template_select(template.select)
    records = selected_records(repository=repository, select=select)

    buckets = owner_buckets(records) if select.mode == TemplateSelectMode.BY_OWNER else ()

    return PlannedSelection(
        template_id=template_id,
        template=template,
        select=select,
        records=records,
        buckets=buckets,
    )


def include_template(
    *,
    template_id: str,
    select: str,
    template_filters: tuple[str, ...],
    select_filters: tuple[str, ...],
) -> bool:
    """Return true when a template should be included by CLI filters."""

    if template_filters and template_id not in template_filters:
        return False

    return not (select_filters and select not in select_filters)