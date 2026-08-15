from __future__ import annotations

from dryv.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity

from ..groups import Contract, walk_groups
from ..schema_resolution import SchemaResolutionError, resolve_effective_schema
from .index import SemanticIndex, owner_span


def validate_schema_extensions(contract: Contract, index: SemanticIndex) -> Diagnostics:
    diagnostics: list[Diagnostic] = []
    for group in walk_groups(contract.groups):
        for schema in group.schemas:
            try:
                resolve_effective_schema(schema.id, index.schemas)
            except SchemaResolutionError as exc:
                diagnostics.append(Diagnostic(code=exc.code, severity=DiagnosticSeverity.ERROR, message=str(exc), span=owner_span(schema), details=(("schema", str(exc.schema)), ("reference", str(exc.reference) if exc.reference is not None else ""))))
    return Diagnostics.from_iterable(diagnostics)


__all__ = ["validate_schema_extensions"]
