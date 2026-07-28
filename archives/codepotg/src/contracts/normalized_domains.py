from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from archives.codepotg.src.contracts.api import ApiContract, ApiOperation, ApiSchema
from archives.codepotg.src.contracts.normalized import (
    ContractCollection,
    ContractDiagnostic,
    ContractReference,
    DiagnosticCategory,
    PresenceValue,
    ReferenceKind,
    SchemaUse,
    contract_collection,
    presence_from_mapping,
)
from archives.codepotg.src.contracts.normalized_builders import build_reference, build_schema_use
from archives.codepotg.src.contracts.source import FrozenMap, freeze_source_map


@dataclass(frozen=True)
class NormalizedServerVariable:
    id: str
    default: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    enum: tuple[Any, ...] = ()
    description: str = "-"

    @property
    def name(self) -> str:
        return self.id


@dataclass(frozen=True)
class NormalizedServer:
    id: str
    url: str
    description: str = "-"
    variables: ContractCollection[NormalizedServerVariable] = field(
        default_factory=ContractCollection
    )

    @property
    def name(self) -> str:
        return self.id


@dataclass(frozen=True)
class NormalizedSecurityScheme:
    id: str
    type: str = "-"
    scheme: str | None = None
    bearer_format: str | None = None
    name_value: str | None = None
    location: str | None = None
    open_id_connect_url: str | None = None
    flows: FrozenMap = field(default_factory=FrozenMap)

    @property
    def name(self) -> str:
        return self.id


@dataclass(frozen=True)
class NormalizedSecurityUse:
    scheme: ContractReference[NormalizedSecurityScheme]
    scopes: tuple[str, ...] = ()


@dataclass(frozen=True)
class NormalizedSecurityRequirement:
    uses: tuple[NormalizedSecurityUse, ...] = ()


@dataclass(frozen=True)
class NormalizedParameter:
    id: str
    location: str = "-"
    description: str = "-"
    required: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    deprecated: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    style: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    explode: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    schema_use: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)

    @property
    def name(self) -> str:
        return self.id


@dataclass(frozen=True)
class NormalizedMediaType:
    id: str
    schema_use: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    example: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    examples: FrozenMap = field(default_factory=FrozenMap)
    encoding: FrozenMap = field(default_factory=FrozenMap)

    @property
    def name(self) -> str:
        return self.id


@dataclass(frozen=True)
class NormalizedRequestBody:
    required: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    description: str = "-"
    content: ContractCollection[NormalizedMediaType] = field(
        default_factory=ContractCollection
    )


@dataclass(frozen=True)
class NormalizedResponse:
    id: str
    description: str = "-"
    content: ContractCollection[NormalizedMediaType] = field(
        default_factory=ContractCollection
    )
    headers: FrozenMap = field(default_factory=FrozenMap)
    links: FrozenMap = field(default_factory=FrozenMap)

    @property
    def name(self) -> str:
        return self.id

    @property
    def is_success(self) -> bool:
        return self.id.isdigit() and 200 <= int(self.id) < 300

    @property
    def is_error(self) -> bool:
        return self.id.isdigit() and int(self.id) >= 400


@dataclass(frozen=True)
class NormalizedPathItem:
    id: str
    summary: str = "-"
    description: str = "-"
    parameters: ContractCollection[NormalizedParameter] = field(
        default_factory=ContractCollection
    )

    @property
    def name(self) -> str:
        return self.id


@dataclass(frozen=True)
class NormalizedOperation:
    id: str
    path: str
    method: str
    summary: str = "-"
    description: str = "-"
    declared_parameters: ContractCollection[NormalizedParameter] = field(
        default_factory=ContractCollection
    )
    effective_parameters: ContractCollection[NormalizedParameter] = field(
        default_factory=ContractCollection
    )
    request_body: NormalizedRequestBody | None = None
    responses: ContractCollection[NormalizedResponse] = field(
        default_factory=ContractCollection
    )
    security: tuple[NormalizedSecurityRequirement, ...] = ()
    security_is_override: bool = False
    callbacks: Mapping[str, FrozenMap] = field(
        default_factory=lambda: MappingProxyType({})
    )

    @property
    def name(self) -> str:
        return self.id

    @property
    def primary_response(self) -> NormalizedResponse | None:
        return next(
            (response for response in self.responses.all if response.is_success),
            self.responses.all[0] if self.responses.all else None,
        )


@dataclass(frozen=True)
class NormalizedAccessPolicy:
    id: str
    public: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    authenticated: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    roles: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    expression: FrozenMap = field(default_factory=FrozenMap)

    @property
    def name(self) -> str:
        return self.id


@dataclass(frozen=True)
class NormalizedEntityField:
    id: str
    type: str | None = None
    required: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    nullable: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    unique: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    readonly: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    backend_only: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    query_operators: tuple[str, ...] = ()
    schema_use: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)

    @property
    def name(self) -> str:
        return self.id


@dataclass(frozen=True)
class NormalizedEntityRelation:
    id: str
    cardinality: str = "-"
    target: ContractReference[Any] = field(
        default_factory=lambda: ContractReference(
            ref="",
            kind=ReferenceKind.ENTITY,
        )
    )
    local_fields: tuple[str, ...] = ()
    foreign_fields: tuple[str, ...] = ()
    on_delete: str | None = None
    on_update: str | None = None

    @property
    def name(self) -> str:
        return self.id

    @property
    def is_to_one(self) -> bool:
        value = self.cardinality.lower().replace("-", "_")
        return value.endswith("_to_one") or value in {
            "one",
            "one_to_one",
            "many_to_one",
        }


@dataclass(frozen=True)
class NormalizedEntityConstraint:
    id: str
    kind: str = "-"
    fields: tuple[str, ...] = ()
    expression: FrozenMap = field(default_factory=FrozenMap)

    @property
    def name(self) -> str:
        return self.id


@dataclass(frozen=True)
class NormalizedEntity:
    id: str
    resource: str | None = None
    table: str | None = None
    abstract: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    schema_use: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    extends: tuple[ContractReference[Any], ...] = ()
    declared_fields: ContractCollection[NormalizedEntityField] = field(
        default_factory=ContractCollection
    )
    backend_fields: ContractCollection[NormalizedEntityField] = field(
        default_factory=ContractCollection
    )
    relations: ContractCollection[NormalizedEntityRelation] = field(
        default_factory=ContractCollection
    )
    constraints: ContractCollection[NormalizedEntityConstraint] = field(
        default_factory=ContractCollection
    )

    @property
    def name(self) -> str:
        return self.id


@dataclass(frozen=True)
class NormalizedFrontendUse:
    alias: str
    operation: ContractReference[ApiOperation] | None = None
    schema: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    purpose: str | None = None


@dataclass(frozen=True)
class NormalizedFrontendComponent:
    id: str
    props: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    uses: tuple[NormalizedFrontendUse, ...] = ()

    @property
    def name(self) -> str:
        return self.id


@dataclass(frozen=True)
class NormalizedFrontendScreen:
    id: str
    route: str = ""
    full_route: str = ""
    params: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    body: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    response: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    components: tuple[str, ...] = ()
    uses: tuple[NormalizedFrontendUse, ...] = ()

    @property
    def name(self) -> str:
        return self.id


@dataclass(frozen=True)
class NormalizedFrontend:
    id: str
    title: str = "-"
    route_prefix: str = ""
    components: ContractCollection[NormalizedFrontendComponent] = field(
        default_factory=ContractCollection
    )
    screens: ContractCollection[NormalizedFrontendScreen] = field(
        default_factory=ContractCollection
    )

    @property
    def name(self) -> str:
        return self.id


@dataclass(frozen=True)
class NormalizedDomainView:
    servers: ContractCollection[NormalizedServer] = field(
        default_factory=ContractCollection
    )
    security_schemes: ContractCollection[NormalizedSecurityScheme] = field(
        default_factory=ContractCollection
    )
    root_security: tuple[NormalizedSecurityRequirement, ...] = ()
    paths: ContractCollection[NormalizedPathItem] = field(
        default_factory=ContractCollection
    )
    operations: ContractCollection[NormalizedOperation] = field(
        default_factory=ContractCollection
    )
    access: ContractCollection[NormalizedAccessPolicy] = field(
        default_factory=ContractCollection
    )
    base_entities: ContractCollection[NormalizedEntity] = field(
        default_factory=ContractCollection
    )
    entities: ContractCollection[NormalizedEntity] = field(
        default_factory=ContractCollection
    )
    frontends: ContractCollection[NormalizedFrontend] = field(
        default_factory=ContractCollection
    )

    @property
    def all_diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        values: list[ContractDiagnostic] = []
        for requirement in self.root_security:
            values.extend(_security_diagnostics(requirement))
        for operation in self.operations.all:
            for requirement in operation.security:
                values.extend(_security_diagnostics(requirement))
            for parameter in operation.effective_parameters.all:
                values.extend(parameter.schema_use.diagnostics)
            if operation.request_body is not None:
                for media in operation.request_body.content.all:
                    values.extend(media.schema_use.diagnostics)
            for response in operation.responses.all:
                for media in response.content.all:
                    values.extend(media.schema_use.diagnostics)
        for entity in (*self.base_entities.all, *self.entities.all):
            values.extend(entity.schema_use.diagnostics)
            for reference in entity.extends:
                values.extend(reference.diagnostics)
            for relation in entity.relations.all:
                values.extend(relation.target.diagnostics)
        for frontend in self.frontends.all:
            for component in frontend.components.all:
                values.extend(component.props.diagnostics)
                values.extend(_use_diagnostics(component.uses))
            for screen in frontend.screens.all:
                values.extend(screen.params.diagnostics)
                values.extend(screen.body.diagnostics)
                values.extend(screen.response.diagnostics)
                values.extend(_use_diagnostics(screen.uses))
        return tuple(values)

    @property
    def unresolved_count(self) -> int:
        return sum(
            diagnostic.category == DiagnosticCategory.UNRESOLVED
            for diagnostic in self.all_diagnostics
        )


def build_normalized_domain_view(
    api: ApiContract,
    raw: Mapping[str, Any] | None,
) -> NormalizedDomainView:
    document = _mapping(raw)
    schema_targets = {schema.ref: schema for schema in api.schemas.all}
    operation_targets = {operation.id: operation for operation in api.operations}

    security_schemes = tuple(
        _security_scheme(str(name), _mapping(value))
        for name, value in _mapping(
            _mapping(document.get("components")).get("securitySchemes")
        ).items()
    )
    security_targets = {item.id: item for item in security_schemes}
    root_security = _security_requirements(
        document.get("security"),
        owner="$",
        source_path="security",
        targets=security_targets,
    )

    paths, operations = _http_domains(
        document,
        root_security=root_security,
        security_targets=security_targets,
        schema_targets=schema_targets,
    )
    codegen = _mapping(document.get("x-codegen"))
    access = tuple(
        _access(str(name), _mapping(value))
        for name, value in _mapping(codegen.get("access")).items()
    )
    base_entities, entities = _entities(
        codegen,
        schema_targets=schema_targets,
    )
    frontends = tuple(
        _frontend(
            str(name),
            _mapping(value),
            schema_targets=schema_targets,
            operation_targets=operation_targets,
        )
        for name, value in _mapping(codegen.get("frontends")).items()
    )
    return NormalizedDomainView(
        servers=contract_collection(
            _server(index, _mapping(value))
            for index, value in enumerate(_sequence(document.get("servers")))
        ),
        security_schemes=contract_collection(security_schemes),
        root_security=root_security,
        paths=contract_collection(paths),
        operations=contract_collection(operations),
        access=contract_collection(access),
        base_entities=contract_collection(base_entities),
        entities=contract_collection(entities),
        frontends=contract_collection(frontends),
    )


def _http_domains(
    document: Mapping[str, Any],
    *,
    root_security: tuple[NormalizedSecurityRequirement, ...],
    security_targets: Mapping[str, NormalizedSecurityScheme],
    schema_targets: Mapping[str, ApiSchema],
) -> tuple[tuple[NormalizedPathItem, ...], tuple[NormalizedOperation, ...]]:
    paths: list[NormalizedPathItem] = []
    operations: list[NormalizedOperation] = []
    for path, value in _mapping(document.get("paths")).items():
        raw_path = _mapping(value)
        path_parameters = _parameters(
            raw_path.get("parameters"),
            owner=str(path),
            source_path=f"paths.{path}.parameters",
            schema_targets=schema_targets,
        )
        paths.append(
            NormalizedPathItem(
                id=str(path),
                summary=_text(raw_path.get("summary")),
                description=_text(raw_path.get("description")),
                parameters=contract_collection(path_parameters),
            )
        )
        for method in _HTTP_METHODS:
            raw_operation = _mapping(raw_path.get(method))
            if raw_operation:
                operations.append(
                    _operation(
                        path=str(path),
                        method=method,
                        raw=raw_operation,
                        path_parameters=path_parameters,
                        root_security=root_security,
                        security_targets=security_targets,
                        schema_targets=schema_targets,
                    )
                )
    return tuple(paths), tuple(operations)


def _server(index: int, raw: Mapping[str, Any]) -> NormalizedServer:
    variables = tuple(
        NormalizedServerVariable(
            id=str(name),
            default=presence_from_mapping(
                _mapping(value),
                "default",
                source_path=f"servers.{index}.variables.{name}",
            ),
            enum=_sequence(_mapping(value).get("enum")),
            description=_text(_mapping(value).get("description")),
        )
        for name, value in _mapping(raw.get("variables")).items()
    )
    return NormalizedServer(
        id=str(index),
        url=str(raw.get("url", "")),
        description=_text(raw.get("description")),
        variables=contract_collection(variables),
    )


def _security_scheme(
    name: str,
    raw: Mapping[str, Any],
) -> NormalizedSecurityScheme:
    return NormalizedSecurityScheme(
        id=name,
        type=str(raw.get("type", "-")),
        scheme=_optional_text(raw.get("scheme")),
        bearer_format=_optional_text(raw.get("bearerFormat")),
        name_value=_optional_text(raw.get("name")),
        location=_optional_text(raw.get("in")),
        open_id_connect_url=_optional_text(raw.get("openIdConnectUrl")),
        flows=freeze_source_map(_mapping(raw.get("flows"))),
    )


def _security_requirements(
    value: Any,
    *,
    owner: str,
    source_path: str,
    targets: Mapping[str, NormalizedSecurityScheme],
) -> tuple[NormalizedSecurityRequirement, ...]:
    return tuple(
        NormalizedSecurityRequirement(
            uses=tuple(
                NormalizedSecurityUse(
                    scheme=build_reference(
                        str(name),
                        kind=ReferenceKind.COMPONENT,
                        owner=owner,
                        source_path=f"{source_path}.{index}.{name}",
                        targets=targets,
                    ),
                    scopes=tuple(str(scope) for scope in _sequence(scopes)),
                )
                for name, scopes in _mapping(item).items()
            )
        )
        for index, item in enumerate(_sequence(value))
    )


def _parameters(
    value: Any,
    *,
    owner: str,
    source_path: str,
    schema_targets: Mapping[str, ApiSchema],
) -> tuple[NormalizedParameter, ...]:
    return tuple(
        _parameter(
            index,
            _mapping(item),
            owner=owner,
            source_path=source_path,
            schema_targets=schema_targets,
        )
        for index, item in enumerate(_sequence(value))
    )


def _parameter(
    index: int,
    raw: Mapping[str, Any],
    *,
    owner: str,
    source_path: str,
    schema_targets: Mapping[str, ApiSchema],
) -> NormalizedParameter:
    return NormalizedParameter(
        id=str(raw.get("name", index)),
        location=str(raw.get("in", "-")),
        description=_text(raw.get("description")),
        required=presence_from_mapping(raw, "required", source_path=source_path),
        deprecated=presence_from_mapping(raw, "deprecated", source_path=source_path),
        style=presence_from_mapping(raw, "style", source_path=source_path),
        explode=presence_from_mapping(raw, "explode", source_path=source_path),
        schema_use=build_schema_use(
            raw.get("schema"),
            owner=owner,
            source_path=f"{source_path}.{index}.schema",
            schema_targets=schema_targets,
        ),
    )


def _operation(
    *,
    path: str,
    method: str,
    raw: Mapping[str, Any],
    path_parameters: tuple[NormalizedParameter, ...],
    root_security: tuple[NormalizedSecurityRequirement, ...],
    security_targets: Mapping[str, NormalizedSecurityScheme],
    schema_targets: Mapping[str, ApiSchema],
) -> NormalizedOperation:
    operation_id = str(raw.get("operationId") or f"{method}:{path}")
    declared = _parameters(
        raw.get("parameters"),
        owner=operation_id,
        source_path=f"paths.{path}.{method}.parameters",
        schema_targets=schema_targets,
    )
    effective = {
        (item.id, item.location): item
        for item in path_parameters
    }
    effective.update({(item.id, item.location): item for item in declared})
    security_is_override = "security" in raw
    security = (
        _security_requirements(
            raw.get("security"),
            owner=operation_id,
            source_path=f"paths.{path}.{method}.security",
            targets=security_targets,
        )
        if security_is_override
        else root_security
    )
    request_body_raw = _mapping(raw.get("requestBody"))
    request_body = (
        _request_body(
            request_body_raw,
            owner=operation_id,
            source_path=f"paths.{path}.{method}.requestBody",
            schema_targets=schema_targets,
        )
        if request_body_raw
        else None
    )
    responses = tuple(
        _response(
            str(status),
            _mapping(value),
            owner=operation_id,
            source_path=f"paths.{path}.{method}.responses.{status}",
            schema_targets=schema_targets,
        )
        for status, value in _mapping(raw.get("responses")).items()
    )
    callbacks = MappingProxyType(
        {
            str(name): freeze_source_map(_mapping(value))
            for name, value in _mapping(raw.get("callbacks")).items()
        }
    )
    return NormalizedOperation(
        id=operation_id,
        path=path,
        method=method,
        summary=_text(raw.get("summary")),
        description=_text(raw.get("description")),
        declared_parameters=contract_collection(declared),
        effective_parameters=contract_collection(effective.values()),
        request_body=request_body,
        responses=contract_collection(responses),
        security=security,
        security_is_override=security_is_override,
        callbacks=callbacks,
    )


def _request_body(
    raw: Mapping[str, Any],
    *,
    owner: str,
    source_path: str,
    schema_targets: Mapping[str, ApiSchema],
) -> NormalizedRequestBody:
    return NormalizedRequestBody(
        required=presence_from_mapping(raw, "required", source_path=source_path),
        description=_text(raw.get("description")),
        content=contract_collection(
            _media_types(
                raw.get("content"),
                owner=owner,
                source_path=f"{source_path}.content",
                schema_targets=schema_targets,
            )
        ),
    )


def _response(
    status: str,
    raw: Mapping[str, Any],
    *,
    owner: str,
    source_path: str,
    schema_targets: Mapping[str, ApiSchema],
) -> NormalizedResponse:
    return NormalizedResponse(
        id=status,
        description=_text(raw.get("description")),
        content=contract_collection(
            _media_types(
                raw.get("content"),
                owner=owner,
                source_path=f"{source_path}.content",
                schema_targets=schema_targets,
            )
        ),
        headers=freeze_source_map(_mapping(raw.get("headers"))),
        links=freeze_source_map(_mapping(raw.get("links"))),
    )


def _media_types(
    value: Any,
    *,
    owner: str,
    source_path: str,
    schema_targets: Mapping[str, ApiSchema],
) -> tuple[NormalizedMediaType, ...]:
    return tuple(
        NormalizedMediaType(
            id=str(content_type),
            schema_use=build_schema_use(
                _mapping(raw).get("schema"),
                owner=owner,
                source_path=f"{source_path}.{content_type}.schema",
                schema_targets=schema_targets,
            ),
            example=presence_from_mapping(
                _mapping(raw),
                "example",
                source_path=f"{source_path}.{content_type}",
            ),
            examples=freeze_source_map(_mapping(_mapping(raw).get("examples"))),
            encoding=freeze_source_map(_mapping(_mapping(raw).get("encoding"))),
        )
        for content_type, raw in _mapping(value).items()
    )


def _access(name: str, raw: Mapping[str, Any]) -> NormalizedAccessPolicy:
    source_path = f"x-codegen.access.{name}"
    return NormalizedAccessPolicy(
        id=name,
        public=presence_from_mapping(raw, "public", source_path=source_path),
        authenticated=presence_from_mapping(
            raw,
            "authenticated",
            source_path=source_path,
        ),
        roles=tuple(str(item) for item in _sequence(raw.get("roles"))),
        permissions=tuple(
            str(item) for item in _sequence(raw.get("permissions"))
        ),
        expression=freeze_source_map(_mapping(raw.get("expression"))),
    )


def _entities(
    codegen: Mapping[str, Any],
    *,
    schema_targets: Mapping[str, ApiSchema],
) -> tuple[tuple[NormalizedEntity, ...], tuple[NormalizedEntity, ...]]:
    base_raw = _mapping(codegen.get("baseEntities"))
    entity_raw = _flatten_entities(_mapping(codegen.get("entities")))
    placeholders = {
        str(name): NormalizedEntity(id=str(name))
        for name in (*base_raw, *entity_raw)
    }
    base_entities = tuple(
        _entity(
            str(name),
            _mapping(value),
            schema_targets=schema_targets,
            entity_targets=placeholders,
            is_base=True,
        )
        for name, value in base_raw.items()
    )
    entities = tuple(
        _entity(
            str(name),
            _mapping(value),
            schema_targets=schema_targets,
            entity_targets=placeholders,
            is_base=False,
        )
        for name, value in entity_raw.items()
    )
    return base_entities, entities


def _entity(
    name: str,
    raw: Mapping[str, Any],
    *,
    schema_targets: Mapping[str, ApiSchema],
    entity_targets: Mapping[str, NormalizedEntity],
    is_base: bool,
) -> NormalizedEntity:
    source_path = f"x-codegen.{'baseEntities' if is_base else 'entities'}.{name}"
    return NormalizedEntity(
        id=name,
        resource=_optional_text(raw.get("resource")),
        table=_optional_text(raw.get("table", raw.get("store"))),
        abstract=presence_from_mapping(raw, "abstract", source_path=source_path),
        schema_use=build_schema_use(
            _schema_value(raw.get("schema")),
            owner=name,
            source_path=f"{source_path}.schema",
            schema_targets=schema_targets,
        ),
        extends=tuple(
            build_reference(
                value,
                kind=ReferenceKind.ENTITY,
                owner=name,
                source_path=f"{source_path}.extends.{index}",
                targets=entity_targets,
            )
            for index, value in enumerate(_string_sequence(raw.get("extends")))
        ),
        declared_fields=contract_collection(
            _entity_field(
                str(field_name),
                _mapping(value),
                source_path=f"{source_path}.fields.{field_name}",
                schema_targets=schema_targets,
                backend_only=False,
            )
            for field_name, value in _named_items(raw.get("fields"))
        ),
        backend_fields=contract_collection(
            _entity_field(
                str(field_name),
                _mapping(value),
                source_path=f"{source_path}.backendFields.{field_name}",
                schema_targets=schema_targets,
                backend_only=True,
            )
            for field_name, value in _named_items(
                raw.get("backendFields", raw.get("backend"))
            )
        ),
        relations=contract_collection(
            _entity_relation(
                str(relation_name),
                _mapping(value),
                owner=name,
                source_path=f"{source_path}.relations.{relation_name}",
                entity_targets=entity_targets,
            )
            for relation_name, value in _named_items(raw.get("relations"))
        ),
        constraints=contract_collection(
            NormalizedEntityConstraint(
                id=str(item_name),
                kind=str(_mapping(value).get("kind", "-")),
                fields=tuple(
                    str(item)
                    for item in _sequence(_mapping(value).get("fields"))
                ),
                expression=freeze_source_map(
                    _mapping(_mapping(value).get("expression"))
                ),
            )
            for item_name, value in _named_items(raw.get("constraints"))
        ),
    )


def _entity_field(
    name: str,
    raw: Mapping[str, Any],
    *,
    source_path: str,
    schema_targets: Mapping[str, ApiSchema],
    backend_only: bool,
) -> NormalizedEntityField:
    query = raw.get("query")
    operators = (
        tuple(str(item) for item in _sequence(query))
        if not isinstance(query, Mapping)
        else tuple(str(item) for item in _sequence(query.get("operators")))
    )
    backend_value = (
        PresenceValue.effective(True, source_path=f"{source_path}.backendOnly")
        if backend_only
        else presence_from_mapping(raw, "backendOnly", source_path=source_path)
    )
    return NormalizedEntityField(
        id=name,
        type=_optional_text(raw.get("type")),
        required=presence_from_mapping(raw, "required", source_path=source_path),
        nullable=presence_from_mapping(raw, "nullable", source_path=source_path),
        unique=presence_from_mapping(raw, "unique", source_path=source_path),
        readonly=presence_from_mapping(raw, "readonly", source_path=source_path),
        backend_only=backend_value,
        query_operators=operators,
        schema_use=build_schema_use(
            _schema_value(raw.get("schema")),
            owner=name,
            source_path=f"{source_path}.schema",
            schema_targets=schema_targets,
        ),
    )


def _entity_relation(
    name: str,
    raw: Mapping[str, Any],
    *,
    owner: str,
    source_path: str,
    entity_targets: Mapping[str, NormalizedEntity],
) -> NormalizedEntityRelation:
    target = str(raw.get("targetEntity", raw.get("target", "")))
    return NormalizedEntityRelation(
        id=name,
        cardinality=str(raw.get("cardinality", raw.get("kind", "-"))),
        target=build_reference(
            target,
            kind=ReferenceKind.ENTITY,
            owner=owner,
            source_path=f"{source_path}.target",
            targets=entity_targets,
        ),
        local_fields=tuple(
            str(item)
            for item in _sequence(raw.get("localFields", raw.get("local")))
        ),
        foreign_fields=tuple(
            str(item)
            for item in _sequence(raw.get("foreignFields", raw.get("foreign")))
        ),
        on_delete=_optional_text(raw.get("onDelete")),
        on_update=_optional_text(raw.get("onUpdate")),
    )


def _frontend(
    name: str,
    raw: Mapping[str, Any],
    *,
    schema_targets: Mapping[str, ApiSchema],
    operation_targets: Mapping[str, ApiOperation],
) -> NormalizedFrontend:
    route_prefix = str(raw.get("routePrefix", raw.get("route", "")))
    components = contract_collection(
        _frontend_component(
            str(component_name),
            _mapping(value),
            owner=f"frontend:{name}:component:{component_name}",
            source_path=f"x-codegen.frontends.{name}.components.{component_name}",
            schema_targets=schema_targets,
            operation_targets=operation_targets,
        )
        for component_name, value in _named_items(raw.get("components"))
    )
    screens = contract_collection(
        _frontend_screen(
            str(screen_name),
            _mapping(value),
            route_prefix=route_prefix,
            owner=f"frontend:{name}:screen:{screen_name}",
            source_path=f"x-codegen.frontends.{name}.screens.{screen_name}",
            schema_targets=schema_targets,
            operation_targets=operation_targets,
        )
        for screen_name, value in _named_items(raw.get("screens"))
    )
    return NormalizedFrontend(
        id=name,
        title=_text(raw.get("title", raw.get("name"))),
        route_prefix=route_prefix,
        components=components,
        screens=screens,
    )


def _frontend_component(
    name: str,
    raw: Mapping[str, Any],
    *,
    owner: str,
    source_path: str,
    schema_targets: Mapping[str, ApiSchema],
    operation_targets: Mapping[str, ApiOperation],
) -> NormalizedFrontendComponent:
    return NormalizedFrontendComponent(
        id=name,
        props=build_schema_use(
            _schema_value(raw.get("props")),
            owner=owner,
            source_path=f"{source_path}.props",
            schema_targets=schema_targets,
        ),
        uses=_frontend_uses(
            raw.get("uses"),
            owner=owner,
            source_path=f"{source_path}.uses",
            schema_targets=schema_targets,
            operation_targets=operation_targets,
        ),
    )


def _frontend_screen(
    name: str,
    raw: Mapping[str, Any],
    *,
    route_prefix: str,
    owner: str,
    source_path: str,
    schema_targets: Mapping[str, ApiSchema],
    operation_targets: Mapping[str, ApiOperation],
) -> NormalizedFrontendScreen:
    route = str(raw.get("route", raw.get("path", "")))
    return NormalizedFrontendScreen(
        id=name,
        route=route,
        full_route=_join_route(route_prefix, route),
        params=build_schema_use(
            _schema_value(raw.get("params")),
            owner=owner,
            source_path=f"{source_path}.params",
            schema_targets=schema_targets,
        ),
        body=build_schema_use(
            _schema_value(raw.get("body")),
            owner=owner,
            source_path=f"{source_path}.body",
            schema_targets=schema_targets,
        ),
        response=build_schema_use(
            _schema_value(raw.get("response")),
            owner=owner,
            source_path=f"{source_path}.response",
            schema_targets=schema_targets,
        ),
        components=tuple(str(item) for item in _sequence(raw.get("components"))),
        uses=_frontend_uses(
            raw.get("uses"),
            owner=owner,
            source_path=f"{source_path}.uses",
            schema_targets=schema_targets,
            operation_targets=operation_targets,
        ),
    )


def _frontend_uses(
    value: Any,
    *,
    owner: str,
    source_path: str,
    schema_targets: Mapping[str, ApiSchema],
    operation_targets: Mapping[str, ApiOperation],
) -> tuple[NormalizedFrontendUse, ...]:
    result: list[NormalizedFrontendUse] = []
    for index, item in enumerate(_sequence(value)):
        raw = _mapping(item)
        operation_name = raw.get("operation", raw.get("operationId"))
        operation = (
            build_reference(
                str(operation_name),
                kind=ReferenceKind.OPERATION,
                owner=owner,
                source_path=f"{source_path}.{index}.operation",
                targets=operation_targets,
            )
            if operation_name is not None
            else None
        )
        result.append(
            NormalizedFrontendUse(
                alias=str(raw.get("alias", raw.get("name", index))),
                operation=operation,
                schema=build_schema_use(
                    _schema_value(raw.get("schema")),
                    owner=owner,
                    source_path=f"{source_path}.{index}.schema",
                    schema_targets=schema_targets,
                ),
                purpose=_optional_text(raw.get("purpose")),
            )
        )
    return tuple(result)


def _security_diagnostics(
    requirement: NormalizedSecurityRequirement,
) -> tuple[ContractDiagnostic, ...]:
    return tuple(
        diagnostic
        for use in requirement.uses
        for diagnostic in use.scheme.diagnostics
    )


def _use_diagnostics(
    uses: tuple[NormalizedFrontendUse, ...],
) -> tuple[ContractDiagnostic, ...]:
    values: list[ContractDiagnostic] = []
    for use in uses:
        if use.operation is not None:
            values.extend(use.operation.diagnostics)
        values.extend(use.schema.diagnostics)
    return tuple(values)


def _flatten_entities(raw: Mapping[str, Any]) -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    entity_keys = {
        "resource",
        "schema",
        "table",
        "store",
        "extends",
        "fields",
        "backend",
        "backendFields",
        "relations",
        "constraints",
        "indexes",
        "unique",
    }
    for name, value in raw.items():
        item = _mapping(value)
        if entity_keys & set(item):
            flattened[str(name)] = value
        else:
            flattened.update(
                {str(nested_name): nested for nested_name, nested in item.items()}
            )
    return flattened


def _named_items(value: Any) -> tuple[tuple[str, Any], ...]:
    if isinstance(value, Mapping):
        return tuple((str(name), item) for name, item in value.items())
    return tuple(
        (str(_mapping(item).get("name", index)), item)
        for index, item in enumerate(_sequence(value))
    )


def _schema_value(value: Any) -> Any:
    return {"$ref": value} if isinstance(value, str) else value


def _string_sequence(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in _sequence(value))


def _join_route(prefix: str, route: str) -> str:
    if not prefix:
        return route or "/"
    if not route:
        return prefix
    return f"/{prefix.strip('/')}/{route.strip('/')}"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> tuple[Any, ...]:
    return tuple(value) if isinstance(value, list | tuple) else ()


def _text(value: Any) -> str:
    return str(value).strip() if value is not None and str(value).strip() else "-"


def _optional_text(value: Any) -> str | None:
    return str(value) if value is not None else None


_HTTP_METHODS = ("get", "put", "post", "delete", "patch", "options", "head", "trace")
