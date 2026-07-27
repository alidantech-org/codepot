from __future__ import annotations

from codepotg.diagnostics import SourceIdentity, SourcePosition, SourceSpan


def from_marks(source: SourceIdentity, start: object, end: object) -> SourceSpan:
    return SourceSpan(
        source=source,
        start=SourcePosition(
            line=int(getattr(start, "line")) + 1,
            column=int(getattr(start, "column")) + 1,
            offset=int(getattr(start, "index")),
        ),
        end=SourcePosition(
            line=int(getattr(end, "line")) + 1,
            column=int(getattr(end, "column")) + 1,
            offset=int(getattr(end, "index")),
        ),
    )


def root_span(source: SourceIdentity, text: str) -> SourceSpan:
    lines = text.splitlines() or [""]
    return SourceSpan(
        source=source,
        start=SourcePosition(1, 1, 0),
        end=SourcePosition(len(lines), len(lines[-1]) + 1, len(text)),
    )
