"""Spec repository indexes."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.contracts.spec.records import SpecRecord
from archives.codepot.src.contracts.spec.refs import SpecRef
from archives.codepot.src.spec.utils.refs import parse_ref


@dataclass(frozen=True)
class SpecRepositoryIndexes:
    """Lookup indexes for normalized spec records."""

    by_id: dict[str, SpecRecord[object]]
    by_ref: dict[str, SpecRecord[object]]
    by_subject: dict[str, tuple[SpecRecord[object], ...]]

    def get_by_id(self, record_id: str) -> SpecRecord[object] | None:
        """Return a record by deterministic runtime id."""

        return self.by_id.get(record_id)

    def resolve(self, ref: SpecRef) -> SpecRecord[object] | None:
        """Resolve a normalized spec ref."""

        return self.by_ref.get(ref.value)

    def records_for_subject(self, subject: str) -> tuple[SpecRecord[object], ...]:
        """Return records for a normalized subject."""

        return self.by_subject.get(subject, ())


def build_indexes(records: tuple[SpecRecord[object], ...]) -> SpecRepositoryIndexes:
    """Build repository lookup indexes."""

    by_id: dict[str, SpecRecord[object]] = {}
    by_ref: dict[str, SpecRecord[object]] = {}
    by_subject: dict[str, list[SpecRecord[object]]] = {}

    for record in records:
        by_id[record.id] = record
        by_ref[record.ref.value] = record
        by_subject.setdefault(record.ref.subject or "", []).append(record)

    return SpecRepositoryIndexes(
        by_id=by_id,
        by_ref=by_ref,
        by_subject={
            subject: tuple(subject_records)
            for subject, subject_records in by_subject.items()
        },
    )


def resolve_ref_key(ref: SpecRef) -> str:
    """Return the key part from a normalized spec ref."""

    return parse_ref(ref).key
