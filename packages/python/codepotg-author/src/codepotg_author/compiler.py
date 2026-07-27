from __future__ import annotations

from dataclasses import dataclass
from types import NoneType, UnionType
from typing import Any, Union, get_args, get_origin

from codepotg.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity
from codepotg.ir import (
    Contract,
    Event,
    EventEffect,
    FieldConstraints,
    Group,
    HttpFacet,
    Name,
    Operation,
    OperationEffects,
    OperationFacets,
    OperationFailure,
    OperationOutput,
    Policy,
    Schema,
    SchemaField,
    SchemaKind,
    SchemaUse,
    SemanticId,
    StorageFieldMapping,
    StorageMapping,
    TypeExpression,
    TypeKind,
    View,
    ViewTrigger,
    Workflow,
    WorkflowDecisionCase,
    WorkflowStep,
    WorkflowStepKind,
    WorkflowTransition,
    validate_contract,
)

from .declarations import Declaration
from .refs import PropertyRef, Ref, RefKind, SchemaRef
from .schemas import (
    FieldDeclaration,
    FieldOptions,
    PropertyDeclaration,
    SchemaDeclaration,
    expand_projection,
)
from .semantics import (
    EventDeclaration,
    OperationDeclaration,
    PolicyDeclaration,
    StorageDeclaration,
    ViewDeclaration,
    WorkflowDeclaration,
    WorkflowStepDeclaration,
)


@dataclass(frozen=True, slots=True)
class AuthoringResult:
    contract: Contract | None
    diagnostics: Diagnostics = Diagnostics()

    @property
    def ok(self) -> bool:
        return self.contract is not None and not self.diagnostics.has_errors


def compile_author(author: Any) -> AuthoringResult:
    try:
        author.freeze()
        declarations = author.declarations
        expanded = _expanded_schemas(declarations)
        ordered = _ordered_schema_declarations(author, declarations, expanded)
        schemas = tuple(_compile_schema(author, item, expanded[item.id]) for item in ordered)
        contract = Contract(
            SemanticId(f"contract/{_slug(author.name)}"),
            Name(author.name),
            _compile_groups(author, declarations, schemas),
            version=author.version,
        )
        diagnostics = validate_contract(contract)
        return AuthoringResult(None if diagnostics.has_errors else contract, diagnostics)
    except Exception as exc:
        diagnostic = Diagnostic(
            code="AUTHOR_COMPILE_FAILED",
            severity=DiagnosticSeverity.ERROR,
            message=str(exc) or exc.__class__.__name__,
            details=(("exception", exc.__class__.__name__),),
        )
        return AuthoringResult(None, Diagnostics.from_iterable((diagnostic,)))


def _expanded_schemas(declarations: tuple[Declaration, ...]) -> dict[str, SchemaDeclaration]:
    raw = {
        item.id: item.payload
        for item in declarations
        if item.kind is RefKind.SCHEMA and isinstance(item.payload, SchemaDeclaration)
    }
    result: dict[str, SchemaDeclaration] = {}
    visiting: set[str] = set()

    def expand(identifier: str) -> SchemaDeclaration:
        if identifier in result:
            return result[identifier]
        if identifier in visiting:
            return raw[identifier]
        visiting.add(identifier)
        declaration = raw[identifier]
        if declaration.source_schema is not None:
            source = expand(declaration.source_schema.declaration_id)
            declaration = SchemaDeclaration(
                declaration.kind,
                fields=expand_projection(source.fields, declaration.projection_steps),
                enum_values=declaration.enum_values,
                alias_of=declaration.alias_of,
            )
        visiting.remove(identifier)
        result[identifier] = declaration
        return declaration

    for identifier in sorted(raw):
        expand(identifier)
    return result


def _ordered_schema_declarations(
    author: Any,
    declarations: tuple[Declaration, ...],
    schemas: dict[str, SchemaDeclaration],
) -> tuple[Declaration, ...]:
    by_id = {item.id: item for item in declarations if item.id in schemas}
    ordered: list[Declaration] = []
    permanent: set[str] = set()
    temporary: set[str] = set()

    def visit(identifier: str) -> None:
        if identifier in permanent or identifier in temporary:
            return
        temporary.add(identifier)
        for dependency in sorted(_schema_dependencies(author, schemas[identifier])):
            if dependency in by_id:
                visit(dependency)
        temporary.remove(identifier)
        permanent.add(identifier)
        ordered.append(by_id[identifier])

    for identifier in sorted(by_id):
        visit(identifier)
    return tuple(ordered)


def _schema_dependencies(author: Any, schema: SchemaDeclaration) -> set[str]:
    result: set[str] = set()
    for item in schema.fields:
        if item.schema_ref is not None:
            result.add(item.schema_ref.declaration_id)
        if item.property_ref is not None:
            property_declaration = author.declaration(item.property_ref)
            if isinstance(property_declaration.payload, PropertyDeclaration):
                result.update(_annotation_dependencies(property_declaration.payload.annotation))
        if item.annotation is not None:
            result.update(_annotation_dependencies(item.annotation))
    return result


def _annotation_dependencies(annotation: object) -> set[str]:
    if isinstance(annotation, SchemaRef):
        return {annotation.declaration_id}
    result: set[str] = set()
    for argument in get_args(annotation):
        result.update(_annotation_dependencies(argument))
    return result


def _compile_schema(author: Any, declaration: Declaration, source: SchemaDeclaration) -> Schema:
    return Schema(
        SemanticId(declaration.id),
        Name(declaration.name),
        SchemaKind(source.kind.value),
        fields=tuple(_compile_field(author, declaration.id, item) for item in source.fields),
        enum_values=source.enum_values,
        alias_of=_type_expression(author, source.alias_of) if source.alias_of is not None else None,
    )


def _compile_field(author: Any, schema_id: str, declaration: FieldDeclaration) -> SchemaField:
    annotation = declaration.annotation
    options = declaration.options
    if declaration.property_ref is not None:
        property_declaration = author.declaration(declaration.property_ref)
        if not isinstance(property_declaration.payload, PropertyDeclaration):
            raise TypeError("property ref does not resolve to a property declaration")
        annotation = property_declaration.payload.annotation
        options = _merge_field_options(property_declaration.payload.options, declaration.options)
    if declaration.schema_ref is not None:
        author.declaration(declaration.schema_ref)
        annotation = declaration.schema_ref
    return SchemaField(
        SemanticId(f"{schema_id}/field/{_slug(declaration.name)}"),
        Name(declaration.name),
        _type_expression(author, annotation),
        required=options.required,
        nullable=options.nullable,
        readonly=options.readonly,
        constraints=FieldConstraints(
            minimum=options.minimum,
            maximum=options.maximum,
            min_length=options.min_length,
            max_length=options.max_length,
            pattern=options.pattern,
            format=options.format,
        ),
    )


def _merge_field_options(base: FieldOptions, override: FieldOptions) -> FieldOptions:
    if override == FieldOptions():
        return base
    return FieldOptions(
        required=override.required,
        nullable=override.nullable,
        readonly=override.readonly,
        minimum=override.minimum if override.minimum is not None else base.minimum,
        maximum=override.maximum if override.maximum is not None else base.maximum,
        min_length=override.min_length if override.min_length is not None else base.min_length,
        max_length=override.max_length if override.max_length is not None else base.max_length,
        pattern=override.pattern or base.pattern,
        format=override.format or base.format,
        description=override.description or base.description,
    )


def _type_expression(author: Any, annotation: object | None) -> TypeExpression:
    if isinstance(annotation, SchemaRef):
        author.declaration(annotation)
        return TypeExpression.reference_to(annotation.declaration_id)
    if isinstance(annotation, PropertyRef):
        declaration = author.declaration(annotation)
        if isinstance(declaration.payload, PropertyDeclaration):
            return _type_expression(author, declaration.payload.annotation)
    primitives: dict[object, str] = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        bytes: "bytes",
        object: "object",
        Any: "unknown",
        NoneType: "null",
    }
    try:
        primitive_name = primitives.get(annotation)
    except TypeError:
        primitive_name = None
    if primitive_name is not None:
        return TypeExpression.primitive(primitive_name)
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin in {list, set, frozenset} and args:
        return TypeExpression.array_of(_type_expression(author, args[0]))
    if origin is dict and len(args) == 2:
        return TypeExpression.map_of(
            _type_expression(author, args[0]),
            _type_expression(author, args[1]),
        )
    if origin is tuple and args:
        members = tuple(_type_expression(author, item) for item in args if item is not Ellipsis)
        return TypeExpression.tuple_of(*members)
    if origin in {UnionType, Union} and args:
        members = tuple(_type_expression(author, item) for item in args)
        return members[0] if len(members) == 1 else TypeExpression.union_of(*members)
    if isinstance(annotation, type):
        return TypeExpression.primitive(annotation.__name__.lower())
    return TypeExpression(TypeKind.UNKNOWN)


def _compile_groups(
    author: Any,
    declarations: tuple[Declaration, ...],
    schemas: tuple[Schema, ...],
) -> tuple[Group, ...]:
    explicit = tuple(item for item in declarations if item.kind is RefKind.GROUP)
    group_ids = tuple(item.id for item in explicit) or ("group/root",)
    group_names = {item.id: item.name for item in explicit} or {"group/root": author.name}
    default_group = group_ids[0]
    declaration_by_id = {item.id: item for item in declarations}
    result: list[Group] = []
    for group_id in group_ids:
        owned = tuple(
            item
            for item in declarations
            if item.kind is not RefKind.GROUP and (item.group_id or default_group) == group_id
        )
        owned_schema_ids = {item.id for item in owned if item.kind is RefKind.SCHEMA}
        result.append(
            Group(
                SemanticId(group_id),
                Name(group_names[group_id]),
                schemas=tuple(item for item in schemas if item.id.value in owned_schema_ids),
                operations=tuple(
                    _compile_operation(author, item)
                    for item in owned
                    if isinstance(item.payload, OperationDeclaration)
                ),
                views=tuple(
                    _compile_view(author, item)
                    for item in owned
                    if isinstance(item.payload, ViewDeclaration)
                ),
                storage_mappings=tuple(
                    _compile_storage(author, item, schemas)
                    for item in owned
                    if isinstance(item.payload, StorageDeclaration)
                ),
                workflows=tuple(
                    _compile_workflow(author, item)
                    for item in owned
                    if isinstance(item.payload, WorkflowDeclaration)
                ),
                policies=tuple(
                    _compile_policy(item)
                    for item in owned
                    if isinstance(item.payload, PolicyDeclaration)
                ),
                events=tuple(
                    _compile_event(author, item)
                    for item in owned
                    if isinstance(item.payload, EventDeclaration)
                ),
            )
        )
    if set(declaration_by_id) != {item.id for item in declarations}:
        raise AssertionError("declaration ids changed during group compilation")
    return tuple(result)


def _sid(author: Any, ref: Ref[Any] | None) -> SemanticId | None:
    if ref is None:
        return None
    author.declaration(ref)
    return SemanticId(ref.declaration_id)


def _compile_operation(author: Any, item: Declaration) -> Operation:
    source = item.payload
    assert isinstance(source, OperationDeclaration)
    http = (
        HttpFacet(source.http_method, source.http_path, source.operation_id)
        if source.http_method and source.http_path
        else None
    )
    return Operation(
        SemanticId(item.id),
        Name(item.name),
        inputs=tuple(
            SchemaUse(
                Name(value.name),
                _require_sid(author, value.schema),
                value.required,
                value.nullable,
                value.readonly,
            )
            for value in source.inputs
        ),
        outputs=tuple(
            OperationOutput(
                Name(value.name) if value.name else None,
                _sid(author, value.schema),
                value.optional,
            )
            for value in source.outputs
        ),
        failures=tuple(
            OperationFailure(value.code, _sid(author, value.schema), value.message)
            for value in source.failures
        ),
        effects=OperationEffects(
            tuple(EventEffect(_require_sid(author, value)) for value in source.emitted_events)
        ),
        facets=OperationFacets(http=http),
    )


def _compile_event(author: Any, item: Declaration) -> Event:
    source = item.payload
    assert isinstance(source, EventDeclaration)
    return Event(
        SemanticId(item.id),
        Name(item.name),
        _sid(author, source.payload_schema),
        _sid(author, source.context_schema),
        source.version,
        source.source,
    )


def _compile_policy(item: Declaration) -> Policy:
    source = item.payload
    assert isinstance(source, PolicyDeclaration)
    return Policy(
        SemanticId(item.id),
        Name(item.name),
        source.roles,
        source.permissions,
        source.scopes,
        source.ownership,
        source.conditions,
    )


def _compile_storage(
    author: Any,
    item: Declaration,
    schemas: tuple[Schema, ...],
) -> StorageMapping:
    source = item.payload
    assert isinstance(source, StorageDeclaration)
    schema_id = _require_sid(author, source.schema)
    schema = next(value for value in schemas if value.id == schema_id)
    fields_by_name = {value.name.raw.original: value for value in schema.fields}

    def field_id(name: str) -> SemanticId:
        if name not in fields_by_name:
            raise ValueError(f"storage references unknown field: {name}")
        return fields_by_name[name].id

    return StorageMapping(
        SemanticId(item.id),
        Name(item.name),
        schema.id,
        source.source,
        fields=tuple(
            StorageFieldMapping(
                field_id(value.field_name),
                value.column,
                value.column_type,
                value.indexed,
                value.unique,
                value.nullable,
            )
            for value in source.fields
        ),
        primary_key=tuple(field_id(name) for name in source.primary_key),
        indexes=tuple(tuple(field_id(name) for name in index) for index in source.indexes),
    )


def _compile_view(author: Any, item: Declaration) -> View:
    source = item.payload
    assert isinstance(source, ViewDeclaration)
    return View(
        SemanticId(item.id),
        Name(item.name),
        _sid(author, source.schema),
        triggers=tuple(
            ViewTrigger(
                Name(value.name),
                _require_sid(author, value.operation),
                value.interaction,
                _sid(author, value.payload_schema),
            )
            for value in source.triggers
        ),
    )


def _compile_workflow(author: Any, item: Declaration) -> Workflow:
    source = item.payload
    assert isinstance(source, WorkflowDeclaration)
    return Workflow(
        SemanticId(item.id),
        Name(item.name),
        inputs=tuple(
            SchemaUse(
                Name(value.name),
                _require_sid(author, value.schema),
                value.required,
                value.nullable,
                value.readonly,
            )
            for value in source.inputs
        ),
        outputs=tuple(
            OperationOutput(
                Name(value.name) if value.name else None,
                _sid(author, value.schema),
                value.optional,
            )
            for value in source.outputs
        ),
        steps=tuple(_compile_workflow_step(author, value) for value in source.steps),
        transitions=tuple(WorkflowTransition(*value) for value in source.transitions),
        failures=tuple(
            OperationFailure(value.code, _sid(author, value.schema), value.message)
            for value in source.failures
        ),
        effects=OperationEffects(
            tuple(EventEffect(_require_sid(author, value)) for value in source.emitted_events)
        ),
        compensation_order=source.compensation_order,
        continue_compensation_on_failure=source.continue_compensation_on_failure,
    )


def _compile_workflow_step(author: Any, source: WorkflowStepDeclaration) -> WorkflowStep:
    return WorkflowStep(
        source.name,
        WorkflowStepKind(source.kind),
        operation=_sid(author, source.operation),
        nested_steps=tuple(_compile_workflow_step(author, item) for item in source.nested_steps),
        decision_cases=tuple(WorkflowDecisionCase(*item) for item in source.decision_cases),
        wait_event=_sid(author, source.wait_event),
        timeout_seconds=source.timeout_seconds,
    )


def _require_sid(author: Any, ref: Ref[Any]) -> SemanticId:
    value = _sid(author, ref)
    assert value is not None
    return value


def _slug(value: str) -> str:
    return "-".join(part.lower() for part in value.replace("_", " ").split())
