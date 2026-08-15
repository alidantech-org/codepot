from __future__ import annotations

from dryv.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity

from ..groups import Contract, walk_groups
from ..types import type_references
from .index import SemanticIndex, owner_span


def validate_property_contract(contract: Contract, index: SemanticIndex) -> Diagnostics:
    diagnostics: list[Diagnostic] = []
    for group in walk_groups(contract.groups):
        for prop in group.properties:
            for reference in type_references(prop.type):
                if reference not in index.schemas:
                    diagnostics.append(Diagnostic(code="IR_MISSING_SCHEMA", severity=DiagnosticSeverity.ERROR, message=f"property {prop.id} references missing schema {reference}", span=owner_span(prop)))
        for schema in group.schemas:
            for schema_field in schema.fields:
                if schema_field.property is not None and schema_field.property not in index.properties:
                    diagnostics.append(Diagnostic(code="IR_MISSING_PROPERTY", severity=DiagnosticSeverity.ERROR, message=f"schema field {schema_field.id} references missing property {schema_field.property}", span=owner_span(schema_field)))
    return Diagnostics.from_iterable(diagnostics)


__all__ = ["validate_property_contract"]
