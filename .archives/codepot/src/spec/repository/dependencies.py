"""Spec repository dependency extraction.

This first version keeps dependency extraction intentionally conservative.
It creates no dependencies until each typed IR dependency shape is wired
explicitly. This avoids guessing object structure or walking unknown values.
"""

from __future__ import annotations

from archives.codepot.src.contracts.spec.dependencies import SpecDependency
from archives.codepot.src.contracts.spec.records import SpecRecord


def extract_dependencies(record: SpecRecord[object]) -> tuple[SpecDependency, ...]:
    """Extract dependencies for one normalized record.

    Dependency extraction must remain typed. Add subject-specific extractors
    here only when the corresponding IR classes are known and directly typed.
    """

    return record.dependencies


def dependencies_for(record: SpecRecord[object]) -> tuple[SpecDependency, ...]:
    """Return dependencies for one normalized record."""

    return extract_dependencies(record)
