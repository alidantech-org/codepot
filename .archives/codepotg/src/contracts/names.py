"""Deterministic naming contract for template variables.

The naming implementation lives in utils.naming. This module only exposes the
stable contract type used by API and template contracts.
"""

from __future__ import annotations

from archives.codepotg.src.utils.naming import build_name
from archives.codepotg.src.utils.naming.provider import NameSet


def make_contract_name(value: str) -> NameSet:
    """Build a contract name using the shared naming provider."""
    return build_name(value)
