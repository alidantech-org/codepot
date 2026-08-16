from __future__ import annotations

from dryv.ir.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity

from ..groups import Contract, walk_groups
from ..schema_resolution import SchemaResolutionError, resolve_effective_schema
from .index import SemanticIndex, owner_span


def validate_storage_facts(contract: Contract, index: SemanticIndex) -> Diagnostics:
    diagnostics: list[Diagnostic] = []
    for group in walk_groups(contract.groups):
        for mapping in group.storage_mappings:
            schema = index.schemas.get(mapping.schema)
            if schema is None:
                continue
            try:
                effective = resolve_effective_schema(schema.id, index.schemas)
            except SchemaResolutionError:
                continue
            field_ids = {item.id for item in effective.fields}
            for role, semantic_id in (
                *(("omitted field", item) for item in mapping.omitted_fields),
                *(("reference field", item.field) for item in mapping.references),
            ):
                if semantic_id not in field_ids:
                    diagnostics.append(_missing("IR_MISSING_FIELD", mapping, role, semantic_id))
            if mapping.version_field is not None and mapping.version_field not in field_ids:
                diagnostics.append(_missing("IR_MISSING_FIELD", mapping, "version field", mapping.version_field))

            columns = {item.column for item in mapping.fields} | {item.column for item in mapping.storage_fields}
            for constraint in mapping.unique_constraints:
                for column in constraint.columns:
                    if column not in columns:
                        diagnostics.append(_missing("IR_MISSING_STORAGE_COLUMN", mapping, f"unique constraint {constraint.name}", column))
            for storage_index in mapping.storage_indexes:
                for column in storage_index.columns:
                    if column not in columns:
                        diagnostics.append(_missing("IR_MISSING_STORAGE_COLUMN", mapping, f"storage index {storage_index.name}", column))

            for reference in mapping.references:
                target = index.storage.get(reference.target_mapping)
                if target is None:
                    diagnostics.append(_missing("IR_MISSING_STORAGE_MAPPING", mapping, "storage reference target", reference.target_mapping))
                    continue
                target_schema = index.schemas.get(target.schema)
                if target_schema is None:
                    continue
                try:
                    target_effective = resolve_effective_schema(target_schema.id, index.schemas)
                except SchemaResolutionError:
                    continue
                if reference.target_field not in {item.id for item in target_effective.fields}:
                    diagnostics.append(_missing("IR_MISSING_FIELD", mapping, "storage reference target field", reference.target_field))
    return Diagnostics.from_iterable(diagnostics)


def _missing(code: str, owner: object, relation: str, value: object) -> Diagnostic:
    return Diagnostic(
        code=code,
        severity=DiagnosticSeverity.ERROR,
        message=f"{relation} references missing value {value}",
        span=owner_span(owner),
        details=(("relation", relation), ("value", str(value))),
    )


__all__ = ["validate_storage_facts"]
