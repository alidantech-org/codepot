"""Stable public diagnostic namespace.

The implementation lives in :mod:`codepotg.core` during the foundation stage so every
adapter and runtime package shares one exact diagnostic type system.
"""

from .core import (
    Diagnostic,
    DiagnosticSeverity,
    Diagnostics,
    RelatedLocation,
    SourceIdentity,
    SourceKind,
    SourcePosition,
    SourceSpan,
)

DiagnosticCollection = Diagnostics

__all__ = [
    "Diagnostic",
    "DiagnosticCollection",
    "DiagnosticSeverity",
    "Diagnostics",
    "RelatedLocation",
    "SourceIdentity",
    "SourceKind",
    "SourcePosition",
    "SourceSpan",
]
