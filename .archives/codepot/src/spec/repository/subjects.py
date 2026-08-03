"""Spec subject mappings."""

from __future__ import annotations

from archives.codepot.src.contracts.spec.records import SpecRecordKind
from archives.codepot.src.spec.utils.enums import SpecSection, SpecSubject


def subject_to_record_kind(subject: SpecSubject) -> SpecRecordKind:
    """Map a repository subject to a normalized record kind."""

    if subject == SpecSubject.URLS:
        return SpecRecordKind.URL
    if subject == SpecSubject.CONTENT_TYPES:
        return SpecRecordKind.CONTENT_TYPE

    if subject == SpecSubject.PRIMITIVES:
        return SpecRecordKind.PRIMITIVE
    if subject == SpecSubject.ENUMS:
        return SpecRecordKind.ENUM
    if subject == SpecSubject.COMPOSITES:
        return SpecRecordKind.COMPOSITE

    if subject == SpecSubject.ENTITIES:
        return SpecRecordKind.ENTITY
    if subject == SpecSubject.FIELD_SETS:
        return SpecRecordKind.FIELD_SET
    if subject == SpecSubject.MODELS:
        return SpecRecordKind.MODEL
    if subject == SpecSubject.DTOS:
        return SpecRecordKind.DTO
    if subject == SpecSubject.PARAMS:
        return SpecRecordKind.PARAMS

    if subject == SpecSubject.RESOURCES:
        return SpecRecordKind.RESOURCE
    if subject == SpecSubject.OPERATIONS:
        return SpecRecordKind.OPERATION
    if subject == SpecSubject.ROUTE_PATHS:
        return SpecRecordKind.ROUTE_PATH
    if subject == SpecSubject.ROUTES:
        return SpecRecordKind.ROUTE

    if subject == SpecSubject.ERRORS:
        return SpecRecordKind.ERROR

    if subject == SpecSubject.SECURITY_CREDENTIALS:
        return SpecRecordKind.SECURITY_CREDENTIAL
    if subject == SpecSubject.SECURITY_PRINCIPALS:
        return SpecRecordKind.SECURITY_PRINCIPAL
    if subject == SpecSubject.SECURITY_POLICIES:
        return SpecRecordKind.SECURITY_POLICY

    raise ValueError(f"Unsupported spec subject: {subject}")


def subject_to_section(subject: SpecSubject) -> SpecSection:
    """Map a repository subject to its physical IR section."""

    if subject == SpecSubject.URLS:
        return SpecSection.URLS
    if subject == SpecSubject.CONTENT_TYPES:
        return SpecSection.CONTENT_TYPES

    if subject == SpecSubject.PRIMITIVES:
        return SpecSection.PROPERTIES_PRIMITIVES
    if subject == SpecSubject.ENUMS:
        return SpecSection.PROPERTIES_ENUMS
    if subject == SpecSubject.COMPOSITES:
        return SpecSection.PROPERTIES_COMPOSITES

    if subject == SpecSubject.ENTITIES:
        return SpecSection.SCHEMAS_ENTITIES
    if subject == SpecSubject.FIELD_SETS:
        return SpecSection.SCHEMAS_FIELD_SETS
    if subject == SpecSubject.MODELS:
        return SpecSection.SCHEMAS_MODELS
    if subject == SpecSubject.DTOS:
        return SpecSection.SCHEMAS_DTOS
    if subject == SpecSubject.PARAMS:
        return SpecSection.SCHEMAS_PARAMS

    if subject == SpecSubject.RESOURCES:
        return SpecSection.RESOURCES
    if subject == SpecSubject.ERRORS:
        return SpecSection.RESPONSES_ERRORS

    if subject == SpecSubject.SECURITY_CREDENTIALS:
        return SpecSection.SECURITY_CREDENTIALS
    if subject == SpecSubject.SECURITY_PRINCIPALS:
        return SpecSection.SECURITY_PRINCIPALS
    if subject == SpecSubject.SECURITY_POLICIES:
        return SpecSection.SECURITY_POLICIES

    if subject in {
        SpecSubject.OPERATIONS,
        SpecSubject.ROUTE_PATHS,
        SpecSubject.ROUTES,
    }:
        return SpecSection.RESOURCES

    raise ValueError(f"Unsupported spec subject section: {subject}")
