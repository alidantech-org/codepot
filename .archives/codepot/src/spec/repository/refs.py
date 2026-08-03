"""Spec repository ref creation."""

from __future__ import annotations

from archives.codepot.src.contracts.spec.refs import SpecRef
from archives.codepot.src.spec.repository.subjects import subject_to_section
from archives.codepot.src.spec.utils.enums import SpecSubject
from archives.codepot.src.spec.utils.refs import build_ref


def create_spec_ref(*, subject: SpecSubject, key: str) -> SpecRef:
    """Create a normalized spec ref for a subject/key pair."""

    section = subject_to_section(subject)
    return build_ref(section=section, key=key, subject=subject)
