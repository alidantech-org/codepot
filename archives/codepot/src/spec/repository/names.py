"""Spec repository name creation."""

from __future__ import annotations

from archives.codepot.src.contracts.spec.names import SpecName
from archives.codepot.src.utils.naming.provider import build_name


def create_spec_name(raw: str) -> SpecName:
    """Create normalized spec name context."""

    return build_name(raw)
