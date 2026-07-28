from __future__ import annotations

from dryv.diagnostics import Diagnostic, DiagnosticSeverity, Diagnostics
from rich.text import Text
from rich.tree import Tree

_SEVERITY_STYLES = {
    DiagnosticSeverity.INFO: ("i", "info"),
    DiagnosticSeverity.WARNING: ("!", "warning"),
    DiagnosticSeverity.ERROR: ("×", "error"),
    DiagnosticSeverity.FATAL: ("×", "fatal"),
}


def diagnostics_tree(diagnostics: Diagnostics) -> Tree:
    root = Tree(Text("diagnostics", style="accent"), guide_style="muted")
    for diagnostic in diagnostics:
        root.add(_diagnostic_tree(diagnostic))
    return root


def _diagnostic_tree(diagnostic: Diagnostic) -> Tree:
    symbol, style = _SEVERITY_STYLES[diagnostic.severity]
    heading = Text()
    heading.append(f"{symbol} ", style=style)
    heading.append(diagnostic.code, style=style)
    heading.append("  ")
    heading.append(diagnostic.message, style="value")
    node = Tree(heading, guide_style="muted")

    if diagnostic.span is not None:
        location = (
            f"{diagnostic.span.source.value}:"
            f"{diagnostic.span.start.line}:{diagnostic.span.start.column}"
        )
        node.add(_label("location", location, "path"))
    for key, value in diagnostic.details:
        node.add(_label(key, str(value), "value"))
    if diagnostic.suggestion:
        node.add(_label("suggestion", diagnostic.suggestion, "success"))
    if diagnostic.documentation:
        node.add(_label("documentation", diagnostic.documentation, "path"))
    return node


def _label(left: str, right: str, right_style: str) -> Text:
    text = Text()
    text.append(left, style="muted")
    text.append(": ", style="muted")
    text.append(right, style=right_style)
    return text
