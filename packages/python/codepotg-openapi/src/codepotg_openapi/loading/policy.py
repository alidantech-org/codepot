from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class SourcePolicy:
    """Host authority for local source access.

    When ``allowed_root`` is absent, an absolute root document may authorize only
    its own parent directory for local references. Relative root locations are
    rejected so behavior never depends on the current working directory.
    """

    allowed_root: Path | None = None
    allow_memory: bool = True

    def canonical_root(self) -> Path | None:
        if self.allowed_root is None:
            return None
        return self.allowed_root.expanduser().resolve(strict=True)
