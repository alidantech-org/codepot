from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DependencyKind(StrEnum):
    EXTENDS = "extends"
    FROM_IMPORT = "from_import"
    IMPORT = "import"
    INCLUDE = "include"


@dataclass(frozen=True, slots=True, order=True)
class DependencyEdge:
    source_id: str
    target_id: str
    kind: DependencyKind
    line: int
