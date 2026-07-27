from __future__ import annotations

from dataclasses import dataclass

from codepotg.diagnostics import SourceSpan


@dataclass(frozen=True, slots=True)
class ParsedNode:
    pointer: str
    value: object
    span: SourceSpan | None
