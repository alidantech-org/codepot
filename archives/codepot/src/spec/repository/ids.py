"""Deterministic spec record id creation."""

from __future__ import annotations

from archives.codepot.src.contracts.spec.refs import SpecOwner
from archives.codepot.src.spec.utils.constants import GLOBAL_OWNER_KEY, IDENTITY_SEPARATOR
from archives.codepot.src.spec.utils.enums import SpecSubject


def _clean_token(value: str) -> str:
    """Normalize one id token."""

    return value.strip().replace("/", IDENTITY_SEPARATOR).replace(" ", "_")


def create_record_id(
    *,
    subject: SpecSubject,
    key: str,
    owner: SpecOwner | None = None,
) -> str:
    """Create a deterministic runtime id for a normalized spec record."""

    subject_token = _clean_token(subject.value)
    key_token = _clean_token(key)

    if owner is None:
        return IDENTITY_SEPARATOR.join((subject_token, key_token))

    owner_token = _clean_token(owner.key or GLOBAL_OWNER_KEY)
    return IDENTITY_SEPARATOR.join((subject_token, owner_token, key_token))
