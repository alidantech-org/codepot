"""Ownership kind mapping helpers."""

from __future__ import annotations

from enum import StrEnum

from archives.codepot.src.spec.utils.enums import SpecSubject


class OwnerIdentityKind(StrEnum):
    """Supported owner identity kinds from dot notation."""

    COMPOSITE = "composite"
    ENTITY = "entity"
    RESOURCE = "resource"
    MODEL = "model"
    DTO = "dto"


def owner_subject_from_identity(value: str) -> SpecSubject | None:
    """Map dot-identity owner kind to repository subject."""

    if value == OwnerIdentityKind.COMPOSITE:
        return SpecSubject.COMPOSITES
    if value == OwnerIdentityKind.ENTITY:
        return SpecSubject.ENTITIES
    if value == OwnerIdentityKind.RESOURCE:
        return SpecSubject.RESOURCES
    if value == OwnerIdentityKind.MODEL:
        return SpecSubject.MODELS
    if value == OwnerIdentityKind.DTO:
        return SpecSubject.DTOS

    return None
