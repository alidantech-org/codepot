from __future__ import annotations

from codepotg.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity

from ..groups import Contract, walk_groups
from ..presentations import Presentation
from ..sources import ValueSource
from .index import SemanticIndex, owner_span


def validate_additional_contract(
    contract: Contract,
    index: SemanticIndex,
) -> Diagnostics:
    diagnostics: list[Diagnostic] = []

    for group in walk_groups(contract.groups):
        for schema in group.schemas:
            field_ids = {item.id for item in schema.fields}
            for field in schema.fields:
                reference = field.capabilities.reference
                if reference is None:
                    continue
                target_schema = index.schemas.get(reference.target_schema)
                if target_schema is None:
                    diagnostics.append(
                        _missing(
                            "IR_MISSING_SCHEMA",
                            "field reference target schema does not exist",
                            field,
                            "schema",
                            str(reference.target_schema),
                        )
                    )
                    continue
                target_fields = {item.id for item in target_schema.fields}
                if reference.target_field not in target_fields:
                    diagnostics.append(
                        _missing(
                            "IR_MISSING_FIELD",
                            "field reference target field does not exist",
                            field,
                            "field",
                            str(reference.target_field),
                        )
                    )
            del field_ids

        for source in group.value_sources:
            _validate_value_source(source, index, diagnostics)

    for presentation in contract.presentations:
        _validate_presentation(presentation, index, diagnostics)

    return Diagnostics.from_iterable(diagnostics)


def _validate_value_source(
    source: ValueSource,
    index: SemanticIndex,
    diagnostics: list[Diagnostic],
) -> None:
    operation = index.operations.get(source.operation)
    if operation is None:
        diagnostics.append(
            _missing(
                "IR_MISSING_OPERATION",
                "value source operation does not exist",
                source,
                "operation",
                str(source.operation),
            )
        )
        return

    output = next(
        (
            item
            for item in operation.outputs
            if item.name is not None and item.name.raw.original == source.output
        ),
        None,
    )
    if output is None:
        diagnostics.append(
            _missing(
                "IR_MISSING_OPERATION_OUTPUT",
                "value source operation output does not exist",
                source,
                "output",
                source.output,
            )
        )
        return
    if output.schema is None:
        diagnostics.append(
            _missing(
                "IR_VALUE_SOURCE_OUTPUT_SCHEMA",
                "value source output must reference a schema",
                source,
                "output",
                source.output,
            )
        )
        return

    schema = index.schemas.get(output.schema)
    if schema is None:
        return
    field_ids = {item.id for item in schema.fields}
    for relation, field_id in (
        ("value", source.value_field),
        *(("label", item) for item in source.label_fields),
    ):
        if field_id not in field_ids:
            diagnostics.append(
                _missing(
                    "IR_MISSING_FIELD",
                    f"value source {relation} field does not belong to its output schema",
                    source,
                    "field",
                    str(field_id),
                )
            )


def _validate_presentation(
    presentation: Presentation,
    index: SemanticIndex,
    diagnostics: list[Diagnostic],
) -> None:
    entry_ids = {item.id for item in presentation.entries}
    addresses: set[str] = set()
    for entry in presentation.entries:
        if entry.view not in index.views:
            diagnostics.append(
                _missing(
                    "IR_MISSING_VIEW",
                    "presentation entry view does not exist",
                    entry,
                    "view",
                    str(entry.view),
                )
            )
        if entry.navigation_parent is not None and entry.navigation_parent not in entry_ids:
            diagnostics.append(
                _missing(
                    "IR_MISSING_PRESENTATION_ENTRY",
                    "presentation navigation parent does not exist",
                    entry,
                    "entry",
                    str(entry.navigation_parent),
                )
            )
        if entry.address is not None:
            if entry.address in addresses:
                diagnostics.append(
                    Diagnostic(
                        code="IR_PRESENTATION_ADDRESS_CONFLICT",
                        severity=DiagnosticSeverity.ERROR,
                        message="presentation addresses must be unique within one presentation",
                        span=owner_span(entry),
                        details=(
                            ("address", entry.address),
                            ("presentation", str(presentation.id)),
                        ),
                    )
                )
            addresses.add(entry.address)


def _missing(
    code: str,
    message: str,
    owner: object,
    detail_key: str,
    detail_value: str,
) -> Diagnostic:
    return Diagnostic(
        code=code,
        severity=DiagnosticSeverity.ERROR,
        message=message,
        span=owner_span(owner),
        details=((detail_key, detail_value),),
    )
