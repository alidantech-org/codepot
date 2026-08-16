from __future__ import annotations

from collections.abc import Iterable

from .console import Console


def render_diagnostics(console: Console, diagnostics: Iterable[object]) -> None:
    for diagnostic in diagnostics:
        if isinstance(diagnostic, dict):
            code = str(diagnostic.get("code", "DIAGNOSTIC"))
            message = str(diagnostic.get("message", ""))
            severity = str(diagnostic.get("severity", diagnostic.get("level", "error")))
            subject = diagnostic.get("subject")
        else:
            code = str(getattr(diagnostic, "code", "DIAGNOSTIC"))
            message = str(getattr(diagnostic, "message", diagnostic))
            severity = str(getattr(diagnostic, "level", "error"))
            subject = getattr(diagnostic, "subject", None)
        suffix = f" [{subject}]" if isinstance(subject, str) and subject else ""
        target = console.error if severity.lower() == "error" else console.write
        target(f"{severity.upper()} {code}{suffix}: {message}")


def render_exception(console: Console, error: Exception) -> None:
    code = str(getattr(error, "code", type(error).__name__))
    message = str(getattr(error, "message", str(error) or type(error).__name__))
    console.error(f"ERROR {code}: {message}")
    diagnostics = getattr(error, "diagnostics", ())
    if diagnostics:
        render_diagnostics(console, diagnostics)
    stderr = getattr(error, "stderr", "")
    if isinstance(stderr, str) and stderr.strip():
        console.error(stderr.rstrip())


__all__ = ["render_diagnostics", "render_exception"]
