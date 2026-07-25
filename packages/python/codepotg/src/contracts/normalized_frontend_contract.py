from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any

from contracts.api import ApiContract, ApiOperation, ApiSchema
from contracts.normalized import (
    ContractCollection,
    ContractDiagnostic,
    ContractReference,
    ReferenceKind,
    SchemaUse,
    SourceObject,
    StructuredNotes,
    contract_collection,
    source_object,
    structured_notes,
)
from contracts.normalized_builders import build_reference, build_schema_use
from contracts.source import FrozenMap, freeze_source_map


@dataclass(frozen=True)
class NormalizedFrontendUseContract:
    alias: str
    operation: ContractReference[ApiOperation] | None = None
    schema: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    purpose: str | None = None
    tags: tuple[str, ...] = ()
    source: SourceObject = field(default_factory=SourceObject)

    @property
    def diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        values = list(self.schema.diagnostics)
        if self.operation is not None:
            values.extend(self.operation.diagnostics)
        return tuple(values)


@dataclass(frozen=True)
class NormalizedFrontendComponentContract:
    id: str
    folder: str | None = None
    props: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    schemas: tuple[SchemaUse[ApiSchema], ...] = ()
    uses: tuple[NormalizedFrontendUseContract, ...] = ()
    tags: tuple[str, ...] = ()
    notes: StructuredNotes = field(default_factory=StructuredNotes)
    source: SourceObject = field(default_factory=SourceObject)

    @property
    def name(self) -> str:
        return self.id

    @property
    def diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        values = tuple(
            diagnostic
            for schema_use in (self.props, *self.schemas)
            for diagnostic in schema_use.diagnostics
        )
        return values + tuple(
            diagnostic
            for use in self.uses
            for diagnostic in use.diagnostics
        )


@dataclass(frozen=True)
class NormalizedFrontendScreenContract:
    id: str
    route: str = ""
    full_route: str = ""
    folder: str | None = None
    params: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    query: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    body: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    response: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    components: tuple[str, ...] = ()
    placement: FrozenMap = field(default_factory=FrozenMap)
    uses: tuple[NormalizedFrontendUseContract, ...] = ()
    tags: tuple[str, ...] = ()
    notes: StructuredNotes = field(default_factory=StructuredNotes)
    source: SourceObject = field(default_factory=SourceObject)

    @property
    def name(self) -> str:
        return self.id

    @property
    def diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        values = tuple(
            diagnostic
            for schema_use in (self.params, self.query, self.body, self.response)
            for diagnostic in schema_use.diagnostics
        )
        return values + tuple(
            diagnostic
            for use in self.uses
            for diagnostic in use.diagnostics
        )


@dataclass(frozen=True)
class NormalizedFrontendContractView:
    id: str
    title: str = "-"
    route_prefix: str = ""
    folders: FrozenMap = field(default_factory=FrozenMap)
    components: ContractCollection[NormalizedFrontendComponentContract] = field(
        default_factory=ContractCollection
    )
    screens: ContractCollection[NormalizedFrontendScreenContract] = field(
        default_factory=ContractCollection
    )
    operations: ContractCollection[ApiOperation] = field(default_factory=ContractCollection)
    schemas: ContractCollection[ApiSchema] = field(default_factory=ContractCollection)
    notes: StructuredNotes = field(default_factory=StructuredNotes)
    source: SourceObject = field(default_factory=SourceObject)

    @property
    def name(self) -> str:
        return self.id

    @property
    def diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        return tuple(
            diagnostic
            for item in (*self.components.all, *self.screens.all)
            for diagnostic in item.diagnostics
        )


@dataclass(frozen=True)
class NormalizedFrontendContract:
    frontends: ContractCollection[NormalizedFrontendContractView] = field(
        default_factory=ContractCollection
    )

    @property
    def all(self) -> tuple[NormalizedFrontendContractView, ...]:
        return self.frontends.all

    @property
    def by_id(self) -> Mapping[str, NormalizedFrontendContractView]:
        return self.frontends.by_id

    @property
    def count(self) -> int:
        return self.frontends.count

    @property
    def diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        return tuple(
            diagnostic
            for frontend in self.frontends.all
            for diagnostic in frontend.diagnostics
        )

    @property
    def unresolved_count(self) -> int:
        return len(self.diagnostics)


def build_normalized_frontend_contract(
    api: ApiContract,
    raw: Mapping[str, Any] | None,
) -> NormalizedFrontendContract:
    """Build explicitly authored frontends without inventing screens or components."""

    document = _mapping(raw)
    frontends_raw = _mapping(_mapping(document.get("x-codegen")).get("frontends"))
    operation_targets = {operation.id: operation for operation in api.operations}
    schema_targets = {schema.ref: schema for schema in api.schemas.all}
    schema_targets.update({schema.id: schema for schema in api.schemas.all})
    values = tuple(
        _frontend(
            str(name),
            _mapping(value),
            operation_targets=operation_targets,
            schema_targets=schema_targets,
        )
        for name, value in frontends_raw.items()
    )
    return NormalizedFrontendContract(frontends=contract_collection(values))


def _frontend(
    name: str,
    raw: Mapping[str, Any],
    *,
    operation_targets: Mapping[str, ApiOperation],
    schema_targets: Mapping[str, ApiSchema],
) -> NormalizedFrontendContractView:
    route_prefix = _route(raw.get("routePrefix", raw.get("route")))
    components = tuple(
        _component(
            str(component_name),
            _mapping(value),
            frontend=name,
            operation_targets=operation_targets,
            schema_targets=schema_targets,
        )
        for component_name, value in _named_items(raw.get("components"))
    )
    screens = tuple(
        _screen(
            str(screen_name),
            _mapping(value),
            frontend=name,
            route_prefix=route_prefix,
            operation_targets=operation_targets,
            schema_targets=schema_targets,
        )
        for screen_name, value in _named_items(raw.get("screens"))
    )
    linked_operations: dict[str, ApiOperation] = {}
    linked_schemas: dict[str, ApiSchema] = {}
    for component in components:
        _collect_schema_uses((component.props, *component.schemas), destination=linked_schemas)
        _collect_uses(component.uses, linked_operations, linked_schemas)
    for screen in screens:
        _collect_schema_uses(
            (screen.params, screen.query, screen.body, screen.response),
            destination=linked_schemas,
        )
        _collect_uses(screen.uses, linked_operations, linked_schemas)
    source_path = f"x-codegen.frontends.{name}"
    return NormalizedFrontendContractView(
        id=name,
        title=_text(raw.get("title", raw.get("name"))),
        route_prefix=route_prefix,
        folders=freeze_source_map(_mapping(raw.get("folders"))),
        components=contract_collection(components),
        screens=contract_collection(screens),
        operations=contract_collection(linked_operations.values()),
        schemas=contract_collection(linked_schemas.values()),
        notes=structured_notes(raw.get("info", raw.get("notes"))),
        source=source_object(raw, source_path=source_path, known_keys=_FRONTEND_KEYS),
    )


def _component(
    name: str,
    raw: Mapping[str, Any],
    *,
    frontend: str,
    operation_targets: Mapping[str, ApiOperation],
    schema_targets: Mapping[str, ApiSchema],
) -> NormalizedFrontendComponentContract:
    source_path = f"x-codegen.frontends.{frontend}.components.{name}"
    return NormalizedFrontendComponentContract(
        id=name,
        folder=_optional_text(raw.get("folder")),
        props=_schema_use(
            raw.get("props"),
            owner=f"frontend:{frontend}:component:{name}",
            source_path=f"{source_path}.props",
            schema_targets=schema_targets,
        ),
        schemas=tuple(
            _schema_use(
                value,
                owner=f"frontend:{frontend}:component:{name}",
                source_path=f"{source_path}.schemas.{index}",
                schema_targets=schema_targets,
            )
            for index, value in enumerate(_sequence(raw.get("schemas")))
        ),
        uses=_uses(
            raw.get("uses"),
            owner=f"frontend:{frontend}:component:{name}",
            source_path=f"{source_path}.uses",
            operation_targets=operation_targets,
            schema_targets=schema_targets,
        ),
        tags=_string_sequence(raw.get("tags")),
        notes=structured_notes(raw.get("info", raw.get("notes"))),
        source=source_object(raw, source_path=source_path, known_keys=_COMPONENT_KEYS),
    )


def _screen(
    name: str,
    raw: Mapping[str, Any],
    *,
    frontend: str,
    route_prefix: str,
    operation_targets: Mapping[str, ApiOperation],
    schema_targets: Mapping[str, ApiSchema],
) -> NormalizedFrontendScreenContract:
    source_path = f"x-codegen.frontends.{frontend}.screens.{name}"
    route = _route(raw.get("route"))
    components, placement = _component_placement(raw.get("components"))
    owner = f"frontend:{frontend}:screen:{name}"
    return NormalizedFrontendScreenContract(
        id=name,
        route=route,
        full_route=_join_route(route_prefix, route),
        folder=_optional_text(raw.get("folder")),
        params=_schema_use(raw.get("params"), owner=owner, source_path=f"{source_path}.params", schema_targets=schema_targets),
        query=_schema_use(raw.get("query"), owner=owner, source_path=f"{source_path}.query", schema_targets=schema_targets),
        body=_schema_use(raw.get("body"), owner=owner, source_path=f"{source_path}.body", schema_targets=schema_targets),
        response=_schema_use(raw.get("response"), owner=owner, source_path=f"{source_path}.response", schema_targets=schema_targets),
        components=components,
        placement=placement,
        uses=_uses(
            raw.get("uses"),
            owner=owner,
            source_path=f"{source_path}.uses",
            operation_targets=operation_targets,
            schema_targets=schema_targets,
        ),
        tags=_string_sequence(raw.get("tags")),
        notes=structured_notes(raw.get("info", raw.get("notes"))),
        source=source_object(raw, source_path=source_path, known_keys=_SCREEN_KEYS),
    )


def _uses(
    value: Any,
    *,
    owner: str,
    source_path: str,
    operation_targets: Mapping[str, ApiOperation],
    schema_targets: Mapping[str, ApiSchema],
) -> tuple[NormalizedFrontendUseContract, ...]:
    values: list[NormalizedFrontendUseContract] = []
    for index, (name, item) in enumerate(_named_items(value)):
        raw = _mapping(item)
        alias = str(raw.get("alias", name))
        operation_name = raw.get("operation", raw.get("operationId"))
        operation = (
            build_reference(
                str(operation_name),
                kind=ReferenceKind.OPERATION,
                owner=owner,
                source_path=f"{source_path}.{index}.operation",
                targets=operation_targets,
            )
            if isinstance(operation_name, str) and operation_name
            else None
        )
        values.append(
            NormalizedFrontendUseContract(
                alias=alias,
                operation=operation,
                schema=_schema_use(
                    raw.get("schema"),
                    owner=owner,
                    source_path=f"{source_path}.{index}.schema",
                    schema_targets=schema_targets,
                ),
                purpose=_optional_text(raw.get("purpose")),
                tags=_string_sequence(raw.get("tags")),
                source=source_object(
                    raw,
                    source_path=f"{source_path}.{index}",
                    known_keys={"name", "alias", "operation", "operationId", "schema", "purpose", "tags"},
                ),
            )
        )
    return tuple(values)


def _collect_uses(
    uses: tuple[NormalizedFrontendUseContract, ...],
    operations: dict[str, ApiOperation],
    schemas: dict[str, ApiSchema],
) -> None:
    for use in uses:
        if use.operation is not None and use.operation.target is not None:
            operations[use.operation.target.id] = use.operation.target
        _collect_schema_uses((use.schema,), destination=schemas)


def _collect_schema_uses(
    values: tuple[SchemaUse[ApiSchema], ...],
    *,
    destination: dict[str, ApiSchema],
) -> None:
    for value in values:
        references = value.refs or ((value.ref,) if value.ref else ())
        for reference in references:
            if reference.target is not None:
                destination[reference.target.id] = reference.target
        if value.schema is not None:
            destination[value.schema.id] = value.schema


def _component_placement(value: Any) -> tuple[tuple[str, ...], FrozenMap]:
    if isinstance(value, Mapping):
        return tuple(str(name) for name in value), freeze_source_map(value)
    return _string_sequence(value), FrozenMap()


def _schema_use(
    value: Any,
    *,
    owner: str,
    source_path: str,
    schema_targets: Mapping[str, ApiSchema],
) -> SchemaUse[ApiSchema]:
    if isinstance(value, str):
        value = {"$ref": value}
    return build_schema_use(value, owner=owner, source_path=source_path, schema_targets=schema_targets)


def _join_route(prefix: str, route: str) -> str:
    parts = [
        part
        for value in (prefix, route)
        for part in PurePosixPath(value).parts
        if part != "/"
    ]
    return "/" + "/".join(parts) if parts else "/"


def _route(value: Any) -> str:
    if not isinstance(value, str) or not value:
        return ""
    return "/" + value.strip("/")


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


def _text(value: Any) -> str:
    return value if isinstance(value, str) and value else "-"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> tuple[Any, ...]:
    return tuple(value) if isinstance(value, list | tuple) else ()


_FRONTEND_KEYS = {"name", "title", "route", "routePrefix", "folders", "components", "screens", "info", "notes"}
_COMPONENT_KEYS = {"name", "folder", "props", "schemas", "uses", "tags", "info", "notes"}
_SCREEN_KEYS = {"name", "route", "folder", "params", "query", "body", "response", "components", "uses", "tags", "info", "notes"}
