from __future__ import annotations

from dryv.ir.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity

from ..base import SemanticId
from ..groups import Contract, walk_groups
from ..schema_resolution import SchemaResolutionError, resolve_effective_schema
from .index import SemanticIndex, owner_span


def validate_value_sources(contract: Contract, index: SemanticIndex) -> Diagnostics:
    diagnostics: list[Diagnostic] = []
    graph: dict[SemanticId, tuple[SemanticId, ...]] = {}
    for group in walk_groups(contract.groups):
        for source in group.value_sources:
            graph[source.id] = tuple(item.source for item in source.dependencies)
            operation = index.operations.get(source.operation)
            if operation is None:
                diagnostics.append(Diagnostic(code="IR_MISSING_OPERATION", severity=DiagnosticSeverity.ERROR, message=f"value source {source.id} references missing operation {source.operation}", span=owner_span(source)))
                continue
            inputs = {item.name.raw.original for item in operation.inputs}
            outputs = {item.name.raw.original: item for item in operation.outputs if item.name is not None}
            output = outputs.get(source.output)
            if output is None:
                diagnostics.append(Diagnostic(code="IR_MISSING_OPERATION_OUTPUT", severity=DiagnosticSeverity.ERROR, message=f"value source {source.id} references missing output {source.output!r} on {operation.id}", span=owner_span(source)))
            if source.search_input is not None and source.search_input not in inputs:
                diagnostics.append(Diagnostic(code="IR_MISSING_OPERATION_INPUT", severity=DiagnosticSeverity.ERROR, message=f"value source {source.id} references missing search input {source.search_input!r} on {operation.id}", span=owner_span(source)))
            for dependency in source.dependencies:
                if dependency.input not in inputs:
                    diagnostics.append(Diagnostic(code="IR_MISSING_OPERATION_INPUT", severity=DiagnosticSeverity.ERROR, message=f"value source {source.id} dependency references missing input {dependency.input!r} on {operation.id}", span=owner_span(source)))
                if dependency.source not in index.value_sources:
                    diagnostics.append(Diagnostic(code="IR_MISSING_VALUE_SOURCE", severity=DiagnosticSeverity.ERROR, message=f"value source {source.id} depends on missing source {dependency.source}", span=owner_span(source)))
            if output is None or output.schema is None:
                continue
            schema = index.schemas.get(output.schema)
            if schema is None:
                continue
            try:
                effective = resolve_effective_schema(schema.id, index.schemas)
            except SchemaResolutionError:
                continue
            fields = {item.id for item in effective.fields}
            for role, field_id in (("value", source.value_field), *(("label", item) for item in source.label_fields)):
                if field_id not in fields:
                    diagnostics.append(Diagnostic(code="IR_MISSING_FIELD", severity=DiagnosticSeverity.ERROR, message=f"value source {source.id} {role} field {field_id} is not in effective output schema {schema.id}", span=owner_span(source)))
    diagnostics.extend(_dependency_cycles(graph, index))
    return Diagnostics.from_iterable(diagnostics)


def _dependency_cycles(graph: dict[SemanticId, tuple[SemanticId, ...]], index: SemanticIndex) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    active: list[SemanticId] = []
    finished: set[SemanticId] = set()
    reported: set[tuple[SemanticId, ...]] = set()

    def visit(source_id: SemanticId) -> None:
        if source_id in finished:
            return
        if source_id in active:
            start = active.index(source_id)
            cycle = tuple((*active[start:], source_id))
            key = tuple(sorted(set(cycle[:-1]), key=str))
            if key not in reported:
                reported.add(key)
                owner = index.value_sources.get(source_id)
                diagnostics.append(Diagnostic(code="IR_VALUE_SOURCE_CYCLE", severity=DiagnosticSeverity.ERROR, message="value source dependency cycle: " + " -> ".join(str(item) for item in cycle), span=owner_span(owner) if owner is not None else None))
            return
        active.append(source_id)
        try:
            for dependency in graph.get(source_id, ()):
                if dependency in graph:
                    visit(dependency)
        finally:
            active.pop()
        finished.add(source_id)

    for source_id in sorted(graph, key=str):
        visit(source_id)
    return diagnostics


__all__ = ["validate_value_sources"]
