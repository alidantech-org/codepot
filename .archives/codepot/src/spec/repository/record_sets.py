"""Typed record set query helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from archives.codepot.src.contracts.spec.records import SpecRecord
from archives.codepot.src.spec.utils.enums import SpecSubject

TData = TypeVar("TData", covariant=True)


@dataclass(frozen=True)
class SpecRecordQuery(Generic[TData]):
    """Read-only query helper over one normalized record collection."""

    subject: SpecSubject
    records: tuple[SpecRecord[TData], ...]

    def all(self) -> tuple[SpecRecord[TData], ...]:
        """Return all records."""

        return self.records

    def first(self) -> SpecRecord[TData] | None:
        """Return the first record when available."""

        if not self.records:
            return None

        return self.records[0]

    def by_key(self, key: str) -> SpecRecord[TData] | None:
        """Return a record by original compiled key."""

        for record in self.records:
            if record.key == key:
                return record

        return None

    def by_id(self, record_id: str) -> SpecRecord[TData] | None:
        """Return a record by deterministic runtime id."""

        for record in self.records:
            if record.id == record_id:
                return record

        return None

    def by_owner_key(self, owner_key: str) -> tuple[SpecRecord[TData], ...]:
        """Return records owned by a specific owner key."""

        return tuple(
            record
            for record in self.records
            if record.owner is not None and record.owner.key == owner_key
        )

    def with_dependencies(self) -> tuple[SpecRecord[TData], ...]:
        """Return records with at least one dependency."""

        return tuple(record for record in self.records if record.dependencies)
