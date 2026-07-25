from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Any

from contracts.api import ApiContract, ApiResource, ApiSchema
from contracts.normalized import (
    ContractCollection,
    ContractDiagnostic,
    ContractReference,
    DiagnosticCategory,
    DiagnosticLevel,
    PresenceValue,
    ReferenceKind,
    SchemaUse,
    SourceObject,
    StructuredNotes,
    contract_collection,
    presence_from_mapping,
    source_object,
    structured_notes,
)
from contracts.normalized_builders import build_reference, build_schema_use
from contracts.source import FrozenMap, freeze_source_map, freeze_source_value


@dataclass(frozen=True)
class NormalizedEntityTarget:
    id: str
    is_base: bool = False

    @property
    def name(self) -> str:
        return self.id


@dataclass(frozen=True)
class NormalizedQueryCapabilities:
    exact: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    one_of: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    sortable: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    selectable: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    date: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    range: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    prefix: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    contains: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    fuzzy: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    operators: tuple[str, ...] = ()
    unknown_operators: tuple[str, ...] = ()
    diagnostics: tuple[ContractDiagnostic, ...] = ()

    @property
    def enabled(self) -> bool:
        return bool(self.operators)


@dataclass(frozen=True)
class NormalizedEntityFieldContract:
    id: str
    type: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    schema_use: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    default: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    constraints: FrozenMap = field(default_factory=FrozenMap)
    role: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    generated: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    unique: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    indexed: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    readonly: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    editable: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    managed: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    immutable: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    selectable: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    backend_only: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    query: NormalizedQueryCapabilities = field(default_factory=NormalizedQueryCapabilities)
    overrides: str | None = None
    override_origin: str | None = None
    source: SourceObject = field(default_factory=SourceObject)

    @property
    def name(self) -> str:
        return self.id

    @property
    def is_backend_only(self) -> bool:
        return self.backend_only.value is True

    @property
    def is_public(self) -> bool:
        return not self.is_backend_only

    @property
    def is_editable(self) -> bool:
        return self.editable.value is True and self.readonly.value is not True

    @property
    def is_queryable(self) -> bool:
        return self.query.enabled

    @property
    def diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        return (
            *self.source.diagnostics,
            *self.schema_use.diagnostics,
            *self.query.diagnostics,
        )


@dataclass(frozen=True)
class NormalizedEntityRelationContract:
    id: str
    cardinality: str = "-"
    target: ContractReference[NormalizedEntityTarget] | None = None
    local_fields: tuple[str, ...] = ()
    foreign_fields: tuple[str, ...] = ()
    on_delete: str | None = None
    on_update: str | None = None
    nullable: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    owning: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    inverse: str | None = None
    source: SourceObject = field(default_factory=SourceObject)

    @property
    def name(self) -> str:
        return self.id

    @property
    def is_to_one(self) -> bool:
        return self.cardinality in {"one_to_one", "many_to_one", "one"}

    @property
    def is_to_many(self) -> bool:
        return self.cardinality in {"one_to_many", "many_to_many", "many"}

    @property
    def diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        return self.target.diagnostics if self.target is not None else ()


@dataclass(frozen=True)
class NormalizedRuleExpression:
    op: str = "unknown"
    field: str | None = None
    value: Any = None
    args: tuple[Any, ...] = ()
    condition: NormalizedRuleExpression | None = None
    then: NormalizedRuleExpression | None = None
    otherwise: NormalizedRuleExpression | None = None
    op_raw: str | None = None
    raw_arguments: FrozenMap = field(default_factory=FrozenMap)
    diagnostics: tuple[ContractDiagnostic, ...] = ()

    @property
    def is_when(self) -> bool:
        return self.op == "when"

    @property
    def is_equal(self) -> bool:
        return self.op in {"eq", "equal", "equals"}

    @property
    def is_not_null(self) -> bool:
        return self.op in {"not_null", "notNull"}


@dataclass(frozen=True)
class NormalizedEntityConstraintContract:
    id: str
    kind: str = "-"
    fields: tuple[str, ...] = ()
    unique: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    rule: NormalizedRuleExpression | None = None
    source: SourceObject = field(default_factory=SourceObject)

    @property
    def name(self) -> str:
        return self.id

    @property
    def diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        return self.rule.diagnostics if self.rule is not None else ()


@dataclass(frozen=True)
class NormalizedEntityContractView:
    id: str
    is_base: bool = False
    resource: ContractReference[ApiResource] | None = None
    schema: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    store: str | None = None
    kind: str | None = None
    abstract: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    visibility: tuple[str, ...] = ()
    extends: tuple[ContractReference[NormalizedEntityTarget], ...] = ()
    declared_fields: ContractCollection[NormalizedEntityFieldContract] = field(
        default_factory=ContractCollection
    )
    inherited_fields: ContractCollection[NormalizedEntityFieldContract] = field(
        default_factory=ContractCollection
    )
    effective_fields: ContractCollection[NormalizedEntityFieldContract] = field(
        default_factory=ContractCollection
    )
    backend_fields: ContractCollection[NormalizedEntityFieldContract] = field(
        default_factory=ContractCollection
    )
    public_fields: ContractCollection[NormalizedEntityFieldContract] = field(
        default_factory=ContractCollection
    )
    storage_fields: ContractCollection[NormalizedEntityFieldContract] = field(
        default_factory=ContractCollection
    )
    editable_fields: ContractCollection[NormalizedEntityFieldContract] = field(
        default_factory=ContractCollection
    )
    readonly_fields: ContractCollection[NormalizedEntityFieldContract] = field(
        default_factory=ContractCollection
    )
    queryable_fields: ContractCollection[NormalizedEntityFieldContract] = field(
        default_factory=ContractCollection
    )
    relations: ContractCollection[NormalizedEntityRelationContract] = field(
        default_factory=ContractCollection
    )
    constraints: ContractCollection[NormalizedEntityConstraintContract] = field(
        default_factory=ContractCollection
    )
    notes: StructuredNotes = field(default_factory=StructuredNotes)
    source: SourceObject = field(default_factory=SourceObject)
    diagnostics: tuple[ContractDiagnostic, ...] = ()

    @property
    def name(self) -> str:
        return self.id

    @property
    def is_abstract(self) -> bool:
        return self.abstract.value is True or self.is_base

    @property
    def is_persistent(self) -> bool:
        return self.store is not None

    @property
    def is_backend_visible(self) -> bool:
        return not self.visibility or "backend" in self.visibility

    @property
    def is_storage_visible(self) -> bool:
        return self.is_persistent and (not self.visibility or "storage" in self.visibility)

    @property
    def all_diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        values = list(self.diagnostics)
        values.extend(self.source.diagnostics)
        values.extend(self.schema.diagnostics)
        for reference in self.extends:
            values.extend(reference.diagnostics)
        for item in self.storage_fields.all:
            values.extend(item.diagnostics)
        for relation in self.relations.all:
            values.extend(relation.diagnostics)
        for constraint in self.constraints.all:
            values.extend(constraint.diagnostics)
        return tuple(values)


@dataclass(frozen=True)
class NormalizedEntityContract:
    base_entities: ContractCollection[NormalizedEntityContractView] = field(
        default_factory=ContractCollection
    )
    entities: ContractCollection[NormalizedEntityContractView] = field(
        default_factory=ContractCollection
    )

    @property
    def all(self) -> tuple[NormalizedEntityContractView, ...]:
        return (*self.base_entities.all, *self.entities.all)

    @property
    def by_id(self) -> Mapping[str, NormalizedEntityContractView]:
        return MappingProxyType({item.id: item for item in self.all})

    @property
    def diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        return tuple(
            diagnostic
            for entity in self.all
            for diagnostic in entity.all_diagnostics
        )

    @property
    def unresolved_count(self) -> int:
        return sum(
            diagnostic.category == DiagnosticCategory.UNRESOLVED
            for diagnostic in self.diagnostics
        )

    @property
    def cycle_count(self) -> int:
        return sum(
            diagnostic.category == DiagnosticCategory.CYCLE
            for diagnostic in self.diagnostics
        )


def build_normalized_entity_contract(
    api: ApiContract,
    raw: Mapping[str, Any] | None,
) -> NormalizedEntityContract:
    """Build inherited entity views after resource/schema registries exist."""

    document = _mapping(raw)
    codegen = _mapping(document.get("x-codegen"))
    base_raw = _mapping(codegen.get("baseEntities"))
    entity_raw = _mapping(codegen.get("entities"))
    all_raw: dict[str, tuple[Mapping[str, Any], bool]] = {
        **{str(name): (_mapping(value), True) for name, value in base_raw.items()},
        **{str(name): (_mapping(value), False) for name, value in entity_raw.items()},
    }
    targets = {
        name: NormalizedEntityTarget(id=name, is_base=is_base)
        for name, (_, is_base) in all_raw.items()
    }
    resource_targets = {resource.id: resource for resource in api.resources}
    schema_targets = {schema.ref: schema for schema in api.schemas.all}
    schema_targets.update({schema.id: schema for schema in api.schemas.all})

    declared = {
        name: _fields(raw_value.get("fields"), owner=name, backend_only=False, schema_targets=schema_targets)
        for name, (raw_value, _) in all_raw.items()
    }
    backend = {
        name: _fields(
            raw_value.get("backendFields", raw_value.get("backend")),
            owner=name,
            backend_only=True,
            schema_targets=schema_targets,
        )
        for name, (raw_value, _) in all_raw.items()
    }
    extends = {
        name: _string_sequence(raw_value.get("extends"))
        for name, (raw_value, _) in all_raw.items()
    }
    cycle_diagnostics: dict[str, list[ContractDiagnostic]] = {
        name: [] for name in all_raw
    }
    effective_cache: dict[str, tuple[NormalizedEntityFieldContract, ...]] = {}

    def effective_fields(
        name: str,
        stack: tuple[str, ...] = (),
    ) -> tuple[NormalizedEntityFieldContract, ...]:
        cached = effective_cache.get(name)
        if cached is not None:
            return cached
        if name in stack:
            cycle = (*stack[stack.index(name):], name)
            cycle_diagnostics[name].append(
                ContractDiagnostic(
                    category=DiagnosticCategory.CYCLE,
                    level=DiagnosticLevel.ERROR,
                    message="Entity inheritance cycle: " + " -> ".join(cycle),
                    source_path=f"x-codegen.entities.{name}.extends",
                    owner=name,
                )
            )
            return ()
        values: list[NormalizedEntityFieldContract] = []
        positions: dict[str, int] = {}
        for parent in extends.get(name, ()):
            if parent not in all_raw:
                continue
            for item in effective_fields(parent, (*stack, name)):
                if item.id not in positions:
                    positions[item.id] = len(values)
                    values.append(item)
        for item in declared.get(name, ()):
            if item.id in positions:
                index = positions[item.id]
                inherited = values[index]
                values[index] = replace(
                    item,
                    overrides=inherited.id,
                    override_origin=extends.get(name, ())[0] if extends.get(name) else None,
                )
            else:
                positions[item.id] = len(values)
                values.append(item)
        result = tuple(values)
        effective_cache[name] = result
        return result

    views: list[NormalizedEntityContractView] = []
    for name, (raw_value, is_base) in all_raw.items():
        inherited = tuple(
            item
            for parent in extends.get(name, ())
            if parent in all_raw
            for item in effective_fields(parent)
        )
        effective = effective_fields(name)
        backend_fields = backend.get(name, ())
        storage = (*effective, *backend_fields)
        references = tuple(
            build_reference(
                parent,
                kind=ReferenceKind.ENTITY,
                owner=name,
                source_path=f"x-codegen.entities.{name}.extends.{index}",
                targets=targets,
            )
            for index, parent in enumerate(extends.get(name, ()))
        )
        resource_name = _optional_text(raw_value.get("resource"))
        resource_reference = (
            build_reference(
                resource_name,
                kind=ReferenceKind.RESOURCE,
                owner=name,
                source_path=f"x-codegen.entities.{name}.resource",
                targets=resource_targets,
            )
            if resource_name is not None
            else None
        )
        views.append(
            NormalizedEntityContractView(
                id=name,
                is_base=is_base,
                resource=resource_reference,
                schema=_schema_use(
                    raw_value.get("schema"),
                    owner=name,
                    source_path=f"x-codegen.entities.{name}.schema",
                    schema_targets=schema_targets,
                ),
                store=_optional_text(raw_value.get("store", raw_value.get("table"))),
                kind=_optional_text(raw_value.get("kind")),
                abstract=presence_from_mapping(
                    raw_value,
                    "abstract",
                    source_path=f"x-codegen.entities.{name}",
                ),
                visibility=_string_sequence(raw_value.get("visibility")),
                extends=references,
                declared_fields=contract_collection(declared.get(name, ())),
                inherited_fields=contract_collection(_dedupe_fields(inherited)),
                effective_fields=contract_collection(effective),
                backend_fields=contract_collection(backend_fields),
                public_fields=contract_collection(item for item in effective if item.is_public),
                storage_fields=contract_collection(storage),
                editable_fields=contract_collection(item for item in effective if item.is_editable),
                readonly_fields=contract_collection(
                    item for item in storage if item.readonly.value is True
                ),
                queryable_fields=contract_collection(
                    item for item in effective if item.is_queryable
                ),
                relations=contract_collection(
                    _relations(
                        raw_value.get("relations"),
                        owner=name,
                        targets=targets,
                    )
                ),
                constraints=contract_collection(
                    _constraints(raw_value, owner=name)
                ),
                notes=structured_notes(raw_value.get("info", raw_value.get("notes"))),
                source=source_object(
                    raw_value,
                    source_path=f"x-codegen.{'baseEntities' if is_base else 'entities'}.{name}",
                    known_keys=_ENTITY_KEYS,
                ),
                diagnostics=tuple(cycle_diagnostics[name]),
            )
        )

    return NormalizedEntityContract(
        base_entities=contract_collection(item for item in views if item.is_base),
        entities=contract_collection(item for item in views if not item.is_base),
    )


def _fields(
    value: Any,
    *,
    owner: str,
    backend_only: bool,
    schema_targets: Mapping[str, ApiSchema],
) -> tuple[NormalizedEntityFieldContract, ...]:
    return tuple(
        _field(
            str(name),
            _mapping(raw),
            owner=owner,
            backend_only=backend_only,
            schema_targets=schema_targets,
        )
        for name, raw in _named_items(value)
    )


def _field(
    name: str,
    raw: Mapping[str, Any],
    *,
    owner: str,
    backend_only: bool,
    schema_targets: Mapping[str, ApiSchema],
) -> NormalizedEntityFieldContract:
    source_path = f"x-codegen.entities.{owner}.{'backendFields' if backend_only else 'fields'}.{name}"
    backend = (
        PresenceValue.effective(True, source_path=f"{source_path}.backendOnly")
        if backend_only
        else presence_from_mapping(raw, "backendOnly", source_path=source_path)
    )
    return NormalizedEntityFieldContract(
        id=name,
        type=presence_from_mapping(raw, "type", source_path=source_path),
        schema_use=_schema_use(
            raw.get("schema"),
            owner=owner,
            source_path=f"{source_path}.schema",
            schema_targets=schema_targets,
        ),
        default=presence_from_mapping(raw, "default", source_path=source_path),
        constraints=freeze_source_map(_mapping(raw.get("constraints"))),
        role=presence_from_mapping(raw, "role", source_path=source_path),
        generated=presence_from_mapping(raw, "generated", source_path=source_path),
        unique=presence_from_mapping(raw, "unique", source_path=source_path),
        indexed=_presence_alias(raw, ("indexed", "index"), source_path),
        readonly=_presence_alias(raw, ("readonly", "readOnly"), source_path),
        editable=presence_from_mapping(raw, "editable", source_path=source_path),
        managed=presence_from_mapping(raw, "managed", source_path=source_path),
        immutable=presence_from_mapping(raw, "immutable", source_path=source_path),
        selectable=presence_from_mapping(raw, "selectable", source_path=source_path),
        backend_only=backend,
        query=_query(raw.get("query"), owner=owner, source_path=f"{source_path}.query"),
        source=source_object(raw, source_path=source_path, known_keys=_FIELD_KEYS),
    )


def _query(
    value: Any,
    *,
    owner: str,
    source_path: str,
) -> NormalizedQueryCapabilities:
    raw = _mapping(value)
    authored = _string_sequence(value) if not raw else _string_sequence(raw.get("operators"))
    flags = {
        "exact": presence_from_mapping(raw, "exact", source_path=source_path),
        "one_of": _presence_alias(raw, ("oneOf", "one_of"), source_path),
        "sortable": _presence_alias(raw, ("sortable", "sort"), source_path),
        "selectable": _presence_alias(raw, ("selectable", "select"), source_path),
        "date": presence_from_mapping(raw, "date", source_path=source_path),
        "range": presence_from_mapping(raw, "range", source_path=source_path),
        "prefix": _nested_presence(raw, "search", "prefix", source_path),
        "contains": _nested_presence(raw, "search", "contains", source_path),
        "fuzzy": _nested_presence(raw, "search", "fuzzy", source_path),
    }
    derived = tuple(name for name, item in flags.items() if item.value is True)
    operators = tuple(dict.fromkeys((*authored, *derived)))
    unknown = tuple(item for item in operators if item not in _KNOWN_QUERY_OPERATORS)
    diagnostics = tuple(
        ContractDiagnostic(
            category=DiagnosticCategory.UNSUPPORTED,
            level=DiagnosticLevel.INFO,
            message=f"Unknown query operator is preserved: {item}",
            source_path=source_path,
            value=item,
            owner=owner,
        )
        for item in unknown
    )
    return NormalizedQueryCapabilities(
        **flags,
        operators=operators,
        unknown_operators=unknown,
        diagnostics=diagnostics,
    )


def _relations(
    value: Any,
    *,
    owner: str,
    targets: Mapping[str, NormalizedEntityTarget],
) -> tuple[NormalizedEntityRelationContract, ...]:
    return tuple(
        _relation(str(name), _mapping(raw), owner=owner, targets=targets)
        for name, raw in _named_items(value)
    )


def _relation(
    name: str,
    raw: Mapping[str, Any],
    *,
    owner: str,
    targets: Mapping[str, NormalizedEntityTarget],
) -> NormalizedEntityRelationContract:
    source_path = f"x-codegen.entities.{owner}.relations.{name}"
    target_name = str(raw.get("targetEntity", raw.get("target", "")))
    return NormalizedEntityRelationContract(
        id=name,
        cardinality=str(raw.get("cardinality", raw.get("kind", "-"))),
        target=build_reference(
            target_name,
            kind=ReferenceKind.ENTITY,
            owner=owner,
            source_path=f"{source_path}.target",
            targets=targets,
        )
        if target_name
        else None,
        local_fields=_field_names(raw.get("localFields", raw.get("local"))),
        foreign_fields=_field_names(raw.get("foreignFields", raw.get("foreign"))),
        on_delete=_optional_text(raw.get("onDelete")),
        on_update=_optional_text(raw.get("onUpdate")),
        nullable=presence_from_mapping(raw, "nullable", source_path=source_path),
        owning=presence_from_mapping(raw, "owning", source_path=source_path),
        inverse=_optional_text(raw.get("inverse", raw.get("inverseField"))),
        source=source_object(raw, source_path=source_path, known_keys=_RELATION_KEYS),
    )


def _constraints(
    raw: Mapping[str, Any],
    *,
    owner: str,
) -> tuple[NormalizedEntityConstraintContract, ...]:
    values: list[NormalizedEntityConstraintContract] = []
    for collection, default_kind in (("constraints", "rule"), ("indexes", "index"), ("unique", "unique")):
        for name, item in _named_items(raw.get(collection)):
            item_raw = _mapping(item)
            source_path = f"x-codegen.entities.{owner}.{collection}.{name}"
            values.append(
                NormalizedEntityConstraintContract(
                    id=str(name),
                    kind=str(item_raw.get("kind", default_kind)),
                    fields=_field_names(item_raw.get("fields", item_raw.get("field"))),
                    unique=(
                        PresenceValue.effective(True, source_path=f"{source_path}.unique")
                        if collection == "unique"
                        else presence_from_mapping(item_raw, "unique", source_path=source_path)
                    ),
                    rule=_rule(item_raw.get("rule", item_raw.get("expression")), source_path=source_path),
                    source=source_object(
                        item_raw,
                        source_path=source_path,
                        known_keys={"kind", "fields", "field", "unique", "rule", "expression"},
                    ),
                )
            )
    return tuple(values)


def _rule(value: Any, *, source_path: str) -> NormalizedRuleExpression | None:
    raw = _mapping(value)
    if not raw:
        return None
    op_raw = str(raw.get("op", raw.get("operation", "unknown")))
    normalized = _RULE_ALIASES.get(op_raw, op_raw)
    diagnostics = ()
    if normalized not in _KNOWN_RULE_OPERATIONS:
        diagnostics = (
            ContractDiagnostic(
                category=DiagnosticCategory.UNSUPPORTED,
                level=DiagnosticLevel.INFO,
                message=f"Unknown rule operation is preserved: {op_raw}",
                source_path=f"{source_path}.op",
                value=op_raw,
            ),
        )
    known = {"op", "operation", "field", "value", "args", "arguments", "condition", "when", "then", "otherwise", "else"}
    return NormalizedRuleExpression(
        op=normalized,
        field=_optional_text(raw.get("field")),
        value=freeze_source_value(raw.get("value")),
        args=tuple(freeze_source_value(item) for item in _sequence(raw.get("args"))),
        condition=_rule(raw.get("condition", raw.get("when")), source_path=f"{source_path}.condition"),
        then=_rule(raw.get("then"), source_path=f"{source_path}.then"),
        otherwise=_rule(raw.get("otherwise", raw.get("else")), source_path=f"{source_path}.otherwise"),
        op_raw=op_raw,
        raw_arguments=freeze_source_map(
            {key: item for key, item in raw.items() if key not in known}
        ),
        diagnostics=diagnostics,
    )


def _schema_use(
    value: Any,
    *,
    owner: str,
    source_path: str,
    schema_targets: Mapping[str, ApiSchema],
) -> SchemaUse[ApiSchema]:
    if isinstance(value, str):
        value = {"$ref": value}
    return build_schema_use(
        value,
        owner=owner,
        source_path=source_path,
        schema_targets=schema_targets,
    )


def _dedupe_fields(
    values: tuple[NormalizedEntityFieldContract, ...],
) -> tuple[NormalizedEntityFieldContract, ...]:
    result: list[NormalizedEntityFieldContract] = []
    positions: dict[str, int] = {}
    for item in values:
        if item.id in positions:
            result[positions[item.id]] = item
        else:
            positions[item.id] = len(result)
            result.append(item)
    return tuple(result)


def _presence_alias(
    raw: Mapping[str, Any],
    keys: tuple[str, ...],
    source_path: str,
) -> PresenceValue[Any]:
    for key in keys:
        if key in raw:
            return PresenceValue.authored(raw[key], source_path=f"{source_path}.{key}")
    return PresenceValue.missing(source_path=f"{source_path}.{keys[0]}")


def _nested_presence(
    raw: Mapping[str, Any],
    parent: str,
    key: str,
    source_path: str,
) -> PresenceValue[Any]:
    nested = _mapping(raw.get(parent))
    return presence_from_mapping(nested, key, source_path=f"{source_path}.{parent}")


def _field_names(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in _sequence(value))


def _named_items(value: Any) -> tuple[tuple[str, Any], ...]:
    if isinstance(value, Mapping):
        return tuple((str(name), item) for name, item in value.items())
    return tuple(
        (str(_mapping(item).get("name", index)), item)
        for index, item in enumerate(_sequence(value))
    )


def _string_sequence(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in _sequence(value))


def _optional_text(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> tuple[Any, ...]:
    return tuple(value) if isinstance(value, list | tuple) else ()


_KNOWN_QUERY_OPERATORS = {
    "exact",
    "one_of",
    "sortable",
    "selectable",
    "date",
    "range",
    "prefix",
    "contains",
    "fuzzy",
}
_KNOWN_RULE_OPERATIONS = {"when", "eq", "equal", "equals", "not_null", "notNull", "and", "or", "not", "in", "range"}
_RULE_ALIASES = {"when": "when", "==": "eq", "not-null": "not_null"}
_ENTITY_KEYS = {
    "resource",
    "schema",
    "store",
    "table",
    "kind",
    "abstract",
    "visibility",
    "extends",
    "fields",
    "backendFields",
    "backend",
    "relations",
    "constraints",
    "indexes",
    "unique",
    "info",
    "notes",
}
_FIELD_KEYS = {
    "type",
    "schema",
    "default",
    "constraints",
    "role",
    "generated",
    "unique",
    "indexed",
    "index",
    "readonly",
    "readOnly",
    "editable",
    "managed",
    "immutable",
    "selectable",
    "backendOnly",
    "query",
}
_RELATION_KEYS = {
    "name",
    "cardinality",
    "kind",
    "targetEntity",
    "target",
    "localFields",
    "local",
    "foreignFields",
    "foreign",
    "onDelete",
    "onUpdate",
    "nullable",
    "owning",
    "inverse",
    "inverseField",
}
