from .model import Diagnostic, DiagnosticSeverity, Diagnostics, RelatedLocation
from .source import SourceIdentity, SourceKind, SourcePosition, SourceSpan

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
