"""Name number classification helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class NumberKind(StrEnum):
    """Detected grammatical number for a token."""

    UNKNOWN = "unknown"
    SINGULAR = "singular"
    PLURAL = "plural"
    INVARIANT = "invariant"


@dataclass(frozen=True)
class NumberForms:
    """Singular and plural forms for a token."""

    original: str
    singular: str
    plural: str
    kind: NumberKind
