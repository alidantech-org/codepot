from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AuthorResult:
    ok: bool
    media_type: str | None
    content: bytes | None
    diagnostics: tuple[dict[str, object], ...]
    ir_version: str | None
    stderr: str = ""


__all__ = ["AuthorResult"]
