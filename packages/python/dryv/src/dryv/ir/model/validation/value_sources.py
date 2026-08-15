from __future__ import annotations

from dryv.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity

from ..groups import Contract, walk_groups
from .index import SemanticIndex, owner_span


def validate_value_sources(contract: Contract, index: SemanticIndex) -> Diagnostics:
    diagnostics: list[Diagnostic] = []
    for group in walk_groups(contract.groups):
        for source in group.value_sources:
            operation = index.operations.get(source.operation)
            if operation is None:
                diagnostics.append(Diagnostic(code="IR_MISSING_OPERATION", severity=DiagnosticSeverity.ERROR, message=f"value source {source.id} references missing operation {source.operation}", span=owner_span(source)))
                continue
            outputs = {item.name.raw.original: item for item in operation.outputs if item.name is not None}
            output = outputs.get(source.output)
            if output is None:
                diagnostics.append(Diagnostic(code="IR_MISSING_OPERATION_OUTPUT", severity=DiagnosticSeverity.ERROR, message=f"value source {source.id} references missing output {source.output!r} on {operation.id}", span=owner_span(source)))
                continue
            if source.search_input is not None:
                inputs = {item.name.raw.original for item in operation.inputs}
                if source.search_input not in inputs:
                    diagnostics.append(Diagnostic(code="IR_MISSING_OPERATION_INPUT", severity=DiagnosticSeverity.ERROR, message=f"value source {source.id} references missing search input {source.search_input!r} on {operation.id}", span=owner_span(source)))
            if output.schema is None:
                continue
            schema = index.schemas.get(output.schema)
            if schema is None:
                continue
            fields = {item.id for item in schema.fields}
            for role, field_id in (("value", source.value_field), *(("label", item) for item in source.label_fields)):
                if field_id not in fields:
                    diagnostics.append(Diagnostic(code="IR_MISSING_FIELD", severity=DiagnosticSeverity.ERROR, message=f"value source {source.id} {role} field {field_id} is not in output schema {schema.id}", span=owner_span(source)))
    return Diagnostics.from_iterable(diagnostics)


__all__ = ["validate_value_sources"]
