from .model import Diagnostic, Diagnostics, DiagnosticSeverity, RelatedLocation
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
