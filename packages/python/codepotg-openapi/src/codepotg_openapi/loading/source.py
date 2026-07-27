from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from codepotg.diagnostics import SourceIdentity


@dataclass(frozen=True, slots=True)
class LoadedSource:
    identity: SourceIdentity
    canonical_id: str
    logical_id: str
    content: bytes
    path: Path | None = None
    authorized_root: Path | None = None
    retrieval_id: str | None = None
