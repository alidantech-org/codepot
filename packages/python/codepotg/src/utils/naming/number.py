"""Name number classification helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class NumberKind(str, Enum):
    """Detected grammatical number for a token."""

    UNKNOWN = "unknown"
    SINGULAR = "singular"
    PLURAL = "plural"
    INVARIANT = "invariant"


@dataclass(frozen=True)
class NumberForms:
    """Original, singular, and plural forms for a token."""

    original: str
    singular: str
    plural: str
    kind: NumberKind
