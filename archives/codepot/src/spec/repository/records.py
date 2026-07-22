"""Spec record creation helpers."""

from __future__ import annotations

from typing import Generic, TypeVar

from archives.codepot.src.contracts.spec.dependencies import SpecDependency
from archives.codepot.src.contracts.spec.records import SpecRecord
from archives.codepot.src.contracts.spec.refs import SpecOwner
from archives.codepot.src.spec.repository.ids import create_record_id
from archives.codepot.src.spec.repository.names import create_spec_name
from archives.codepot.src.spec.repository.ownership import create_global_owner, create_spec_identity
from archives.codepot.src.spec.repository.refs import create_spec_ref
from archives.codepot.src.spec.repository.subjects import subject_to_record_kind
from archives.codepot.src.spec.utils.enums import SpecSubject

TData = TypeVar("TData")


def create_spec_record(
    *,
    subject: SpecSubject,
    key: str,
    data: TData,
    owner: SpecOwner | None = None,
    dependencies: tuple[SpecDependency, ...] = (),
) -> SpecRecord[TData]:
    """Create a normalized spec record around typed IR data."""

    identity = create_spec_identity(key)
    normalized_owner = owner or create_global_owner()

    return SpecRecord(
        id=create_record_id(subject=subject, key=key, owner=normalized_owner),
        kind=subject_to_record_kind(subject),
        key=key,
        ref=create_spec_ref(subject=subject, key=key),
        identity=identity,
        name=create_spec_name(identity.local_key),
        data=data,
        owner=normalized_owner,
        dependencies=dependencies,
    )


class TypedSpecRecord(Generic[TData]):
    """Typing marker for typed spec records.

    This class is intentionally empty. It is useful for explicit type aliases
    later without adding behavior to the record contract.
    """
