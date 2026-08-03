from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from archives.codepotg.src.contracts.api import (
    ApiContract,
    ApiEntity,
    ApiOperation,
    ApiResource,
    ApiSchema,
)
from archives.codepotg.src.contracts.normalized import (
    ContractCollection,
    ContractDiagnostic,
    ContractReference,
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
from archives.codepotg.src.contracts.normalized_builders import build_reference, build_schema_use
from archives.codepotg.src.contracts.normalized_domains import (
    NormalizedAccessPolicy,
    NormalizedDomainView,
)
from archives.codepotg.src.contracts.source import FrozenMap, freeze_source_map


@dataclass(frozen=True)
class NormalizedUiSettings:
    enabled: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    infer: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    inferred: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    role: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    source: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    reason: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    effective_enabled: PresenceValue[Any] = field(default_factory=PresenceValue.missing)


@dataclass(frozen=True)
class NormalizedAccessUse:
    ref: str | None = None
    policy: ContractReference[NormalizedAccessPolicy] | None = None
    source: SourceObject = field(default_factory=SourceObject)

    @property
    def is_resolved(self) -> bool:
        return self.policy is not None and self.policy.is_resolved

    @property
    def diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        return self.policy.diagnostics if self.policy is not None else ()


@dataclass(frozen=True)
class NormalizedCacheRead:
    enabled: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    ttl_seconds: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    stale_seconds: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    scope: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    key_fields: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class NormalizedCacheInvalidation:
    operation_names: tuple[str, ...] = ()
    operations: tuple[ContractReference[ApiOperation], ...] = ()
    resource_names: tuple[str, ...] = ()
    resources: tuple[ContractReference[ApiResource], ...] = ()
    tags: tuple[str, ...] = ()
    all: PresenceValue[Any] = field(default_factory=PresenceValue.missing)

    @property
    def diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        return tuple(
            diagnostic
            for reference in (*self.operations, *self.resources)
            for diagnostic in reference.diagnostics
        )


@dataclass(frozen=True)
class NormalizedCachePolicy:
    enabled: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    read: NormalizedCacheRead = field(default_factory=NormalizedCacheRead)
    invalidate: NormalizedCacheInvalidation = field(default_factory=NormalizedCacheInvalidation)
    source: SourceObject = field(default_factory=SourceObject)


@dataclass(frozen=True)
class NormalizedTransportInbound:
    ip: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    user_agent: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    headers: FrozenMap = field(default_factory=FrozenMap)
    cookies: FrozenMap = field(default_factory=FrozenMap)


@dataclass(frozen=True)
class NormalizedTransportOutbound:
    headers: FrozenMap = field(default_factory=FrozenMap)
    cookies: FrozenMap = field(default_factory=FrozenMap)


@dataclass(frozen=True)
class NormalizedRuntimeTransport:
    inbound: NormalizedTransportInbound = field(default_factory=NormalizedTransportInbound)
    outbound: NormalizedTransportOutbound = field(default_factory=NormalizedTransportOutbound)


@dataclass(frozen=True)
class NormalizedHookDefinition:
    id: str
    resource: str
    handler: str | None = None
    order: int = 0
    notes: StructuredNotes = field(default_factory=StructuredNotes)
    source: SourceObject = field(default_factory=SourceObject)

    @property
    def name(self) -> str:
        return self.id

    @property
    def ref(self) -> str:
        return f"{self.resource}.{self.id}"


@dataclass(frozen=True)
class NormalizedHookUse:
    ref: str
    hook: ContractReference[NormalizedHookDefinition]
    phase: str
    order: int
    source: SourceObject = field(default_factory=SourceObject)

    @property
    def is_resolved(self) -> bool:
        return self.hook.is_resolved

    @property
    def diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        return self.hook.diagnostics


@dataclass(frozen=True)
class NormalizedRuntimeHooks:
    before_handler: tuple[NormalizedHookUse, ...] = ()
    after_success: tuple[NormalizedHookUse, ...] = ()
    after_error: tuple[NormalizedHookUse, ...] = ()

    @property
    def all(self) -> tuple[NormalizedHookUse, ...]:
        return (*self.before_handler, *self.after_success, *self.after_error)


@dataclass(frozen=True)
class NormalizedDataSource:
    id: str
    response_field: str | None = None
    item: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    key_field: str | None = None
    label_field: str | None = None
    value_field: str | None = None
    description: str = "-"
    primary: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    source: SourceObject = field(default_factory=SourceObject)

    @property
    def name(self) -> str:
        return self.id


@dataclass(frozen=True)
class NormalizedOperationMetadata:
    id: str
    name_value: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    role: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    tags: tuple[str, ...] = ()
    ui: NormalizedUiSettings = field(default_factory=NormalizedUiSettings)
    parameter_target: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    query_schema: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    params_schema: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    body_schema: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    response_schema: SchemaUse[ApiSchema] = field(default_factory=SchemaUse)
    sources: ContractCollection[NormalizedDataSource] = field(default_factory=ContractCollection)
    primary_source: NormalizedDataSource | None = None
    cache: NormalizedCachePolicy = field(default_factory=NormalizedCachePolicy)
    access: NormalizedAccessUse = field(default_factory=NormalizedAccessUse)
    transport: NormalizedRuntimeTransport = field(default_factory=NormalizedRuntimeTransport)
    hooks: NormalizedRuntimeHooks = field(default_factory=NormalizedRuntimeHooks)
    notes: StructuredNotes = field(default_factory=StructuredNotes)
    source: SourceObject = field(default_factory=SourceObject)

    @property
    def name(self) -> str:
        return self.id

    @property
    def role_origin(self) -> str:
        return self.role.origin.value

    @property
    def diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        values = list(self.cache.invalidate.diagnostics)
        values.extend(self.access.diagnostics)
        for hook in self.hooks.all:
            values.extend(hook.diagnostics)
        for data_source in self.sources.all:
            values.extend(data_source.item.diagnostics)
        for schema_use in (
            self.parameter_target,
            self.query_schema,
            self.params_schema,
            self.body_schema,
            self.response_schema,
        ):
            values.extend(schema_use.diagnostics)
        return tuple(values)


@dataclass(frozen=True)
class NormalizedResourceMetadata:
    id: str
    route: str | None = None
    tags: tuple[str, ...] = ()
    ui: NormalizedUiSettings = field(default_factory=NormalizedUiSettings)
    access_policies: tuple[ContractReference[NormalizedAccessPolicy], ...] = ()
    hooks: ContractCollection[NormalizedHookDefinition] = field(default_factory=ContractCollection)
    operations: ContractCollection[ApiOperation] = field(default_factory=ContractCollection)
    schemas: ContractCollection[ApiSchema] = field(default_factory=ContractCollection)
    entities: ContractCollection[ApiEntity] = field(default_factory=ContractCollection)
    notes: StructuredNotes = field(default_factory=StructuredNotes)
    source: SourceObject = field(default_factory=SourceObject)

    @property
    def name(self) -> str:
        return self.id

    @property
    def diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        return tuple(
            diagnostic
            for reference in self.access_policies
            for diagnostic in reference.diagnostics
        )


@dataclass(frozen=True)
class NormalizedCodegenContract:
    resources: ContractCollection[NormalizedResourceMetadata] = field(default_factory=ContractCollection)
    operations: ContractCollection[NormalizedOperationMetadata] = field(default_factory=ContractCollection)
    hooks: ContractCollection[NormalizedHookDefinition] = field(default_factory=ContractCollection)

    @property
    def diagnostics(self) -> tuple[ContractDiagnostic, ...]:
        return tuple(
            diagnostic
            for item in (*self.resources.all, *self.operations.all)
            for diagnostic in item.diagnostics
        )

    @property
    def unresolved_count(self) -> int:
        return len(self.diagnostics)


def build_normalized_codegen_contract(
    api: ApiContract,
    raw: Mapping[str, Any] | None,
    domains: NormalizedDomainView,
) -> NormalizedCodegenContract:
    document = _mapping(raw)
    codegen = _mapping(document.get("x-codegen"))
    resources_raw = _mapping(codegen.get("resources"))
    policy_targets = {item.id: item for item in domains.access.all}
    resource_targets = {item.id: item for item in api.resources}
    operation_targets = {item.id: item for item in api.operations}
    schema_targets = {item.ref: item for item in api.schemas.all}
    schema_targets.update({item.id: item for item in api.schemas.all})

    hook_definitions = tuple(
        hook
        for resource_name, value in resources_raw.items()
        for hook in _resource_hooks(str(resource_name), _mapping(value))
    )
    hook_targets: dict[str, NormalizedHookDefinition] = {}
    for hook in hook_definitions:
        hook_targets[hook.ref] = hook
        hook_targets.setdefault(hook.id, hook)

    resources = tuple(
        _resource(
            resource,
            _mapping(resources_raw.get(resource.id)),
            api=api,
            policy_targets=policy_targets,
            hooks=tuple(item for item in hook_definitions if item.resource == resource.id),
        )
        for resource in api.resources
    )
    resource_ui = {item.id: item.ui for item in resources}
    operations = tuple(
        _operation(
            operation,
            _operation_raw(document, operation),
            resource_ui=resource_ui.get(operation.resource or ""),
            policy_targets=policy_targets,
            resource_targets=resource_targets,
            operation_targets=operation_targets,
            schema_targets=schema_targets,
            hook_targets=hook_targets,
        )
        for operation in api.operations
    )
    return NormalizedCodegenContract(
        resources=contract_collection(resources),
        operations=contract_collection(operations),
        hooks=contract_collection(hook_definitions),
    )


def _resource(
    resource: ApiResource,
    raw: Mapping[str, Any],
    *,
    api: ApiContract,
    policy_targets: Mapping[str, NormalizedAccessPolicy],
    hooks: tuple[NormalizedHookDefinition, ...],
) -> NormalizedResourceMetadata:
    source_path = f"x-codegen.resources.{resource.id}"
    policy_names = _string_sequence(raw.get("accessPolicies", raw.get("access")))
    return NormalizedResourceMetadata(
        id=resource.id,
        route=_optional_text(raw.get("route")),
        tags=_string_sequence(raw.get("tags")),
        ui=_ui(_mapping(raw.get("ui")), source_path=f"{source_path}.ui"),
        access_policies=tuple(
            build_reference(
                name,
                kind=ReferenceKind.ACCESS,
                owner=resource.id,
                source_path=f"{source_path}.accessPolicies.{index}",
                targets=policy_targets,
            )
            for index, name in enumerate(policy_names)
        ),
        hooks=contract_collection(hooks),
        operations=contract_collection(item for item in api.operations if item.resource == resource.id),
        schemas=contract_collection(item for item in api.schemas.all if item.resource == resource.id),
        entities=contract_collection(item for item in api.entities if item.resource == resource.id),
        notes=structured_notes(raw.get("info", raw.get("notes"))),
        source=source_object(raw, source_path=source_path, known_keys=_RESOURCE_KEYS),
    )


def _resource_hooks(resource: str, raw: Mapping[str, Any]) -> tuple[NormalizedHookDefinition, ...]:
    return tuple(
        NormalizedHookDefinition(
            id=str(name),
            resource=resource,
            handler=_optional_text(_mapping(value).get("handler")),
            order=_integer(_mapping(value).get("order"), default=index),
            notes=structured_notes(_mapping(value).get("info", _mapping(value).get("notes"))),
            source=source_object(
                _mapping(value),
                source_path=f"x-codegen.resources.{resource}.hooks.{name}",
                known_keys={"handler", "order", "info", "notes"},
            ),
        )
        for index, (name, value) in enumerate(_mapping(raw.get("hooks")).items())
    )


def _operation(
    operation: ApiOperation,
    raw: Mapping[str, Any],
    *,
    resource_ui: NormalizedUiSettings | None,
    policy_targets: Mapping[str, NormalizedAccessPolicy],
    resource_targets: Mapping[str, ApiResource],
    operation_targets: Mapping[str, ApiOperation],
    schema_targets: Mapping[str, ApiSchema],
    hook_targets: Mapping[str, NormalizedHookDefinition],
) -> NormalizedOperationMetadata:
    source_path = f"paths.{operation.path}.{operation.method}.x-codegen"
    parameter_raw = _mapping(raw.get("parameters"))
    sources = tuple(
        _data_source(
            str(name),
            _mapping(value),
            owner=operation.id,
            source_path=f"{source_path}.sources.{name}",
            schema_targets=schema_targets,
        )
        for name, value in _named_items(raw.get("sources"))
    )
    return NormalizedOperationMetadata(
        id=operation.id,
        name_value=presence_from_mapping(raw, "name", source_path=source_path),
        role=_operation_role(operation, raw, source_path=source_path),
        tags=_string_sequence(raw.get("tags")),
        ui=_ui(_mapping(raw.get("ui")), source_path=f"{source_path}.ui", inherited=resource_ui),
        parameter_target=_schema_use(parameter_raw.get("target", raw.get("target")), owner=operation.id, source_path=f"{source_path}.parameters.target", schema_targets=schema_targets),
        query_schema=_schema_use(raw.get("query"), owner=operation.id, source_path=f"{source_path}.query", schema_targets=schema_targets),
        params_schema=_schema_use(raw.get("params"), owner=operation.id, source_path=f"{source_path}.params", schema_targets=schema_targets),
        body_schema=_schema_use(raw.get("body"), owner=operation.id, source_path=f"{source_path}.body", schema_targets=schema_targets),
        response_schema=_schema_use(raw.get("response"), owner=operation.id, source_path=f"{source_path}.response", schema_targets=schema_targets),
        sources=contract_collection(sources),
        primary_source=next((item for item in sources if item.primary.value is True), sources[0] if sources else None),
        cache=_cache(_mapping(raw.get("cache")), owner=operation.id, source_path=f"{source_path}.cache", operation_targets=operation_targets, resource_targets=resource_targets),
        access=_access_use(raw.get("access"), owner=operation.id, source_path=f"{source_path}.access", policy_targets=policy_targets),
        transport=_transport(_mapping(_mapping(raw.get("runtime")).get("transport"))),
        hooks=_hook_uses(
            _mapping(_mapping(raw.get("runtime")).get("hooks", raw.get("hooks"))),
            owner=operation.id,
            source_path=f"{source_path}.runtime.hooks",
            resource=operation.resource,
            hook_targets=hook_targets,
        ),
        notes=structured_notes(raw.get("info", raw.get("notes"))),
        source=source_object(raw, source_path=source_path, known_keys=_OPERATION_KEYS),
    )


def _operation_role(operation: ApiOperation, raw: Mapping[str, Any], *, source_path: str) -> PresenceValue[Any]:
    if "role" in raw:
        return PresenceValue.authored(raw["role"], source_path=f"{source_path}.role")
    if operation.target is not None and operation.target.inferred_roles:
        return PresenceValue.inferred(operation.target.inferred_roles[0], source_path=f"{source_path}.role")
    inferred = {"get": "query", "post": "create", "put": "update", "patch": "update", "delete": "delete"}.get(str(operation.method), "unknown")
    return PresenceValue.inferred(inferred, source_path=f"{source_path}.role")


def _ui(raw: Mapping[str, Any], *, source_path: str, inherited: NormalizedUiSettings | None = None) -> NormalizedUiSettings:
    enabled = presence_from_mapping(raw, "enabled", source_path=source_path)
    inherited_enabled = inherited.effective_enabled if inherited is not None else None
    if enabled.is_set:
        effective = PresenceValue.effective(enabled.value, source_path=f"{source_path}.effective")
    elif inherited_enabled is not None and inherited_enabled.is_set:
        effective = inherited_enabled
    else:
        effective = PresenceValue.missing(source_path=f"{source_path}.effective")
    return NormalizedUiSettings(
        enabled=enabled,
        infer=presence_from_mapping(raw, "infer", source_path=source_path),
        inferred=presence_from_mapping(raw, "inferred", source_path=source_path),
        role=presence_from_mapping(raw, "role", source_path=source_path),
        source=presence_from_mapping(raw, "source", source_path=source_path),
        reason=presence_from_mapping(raw, "reason", source_path=source_path),
        effective_enabled=effective,
    )


def _access_use(value: Any, *, owner: str, source_path: str, policy_targets: Mapping[str, NormalizedAccessPolicy]) -> NormalizedAccessUse:
    raw = _mapping(value)
    ref = value if isinstance(value, str) else raw.get("ref", raw.get("policy"))
    if not isinstance(ref, str) or not ref:
        return NormalizedAccessUse(source=source_object(raw, source_path=source_path, known_keys={"ref", "policy"}))
    return NormalizedAccessUse(
        ref=ref,
        policy=build_reference(ref, kind=ReferenceKind.ACCESS, owner=owner, source_path=source_path, targets=policy_targets),
        source=source_object(raw, source_path=source_path, known_keys={"ref", "policy"}),
    )


def _cache(
    raw: Mapping[str, Any],
    *,
    owner: str,
    source_path: str,
    operation_targets: Mapping[str, ApiOperation],
    resource_targets: Mapping[str, ApiResource],
) -> NormalizedCachePolicy:
    read = _mapping(raw.get("read"))
    invalidate = _mapping(raw.get("invalidate"))
    operation_names = _string_sequence(invalidate.get("operations", invalidate.get("operationNames")))
    resource_names = _string_sequence(invalidate.get("resources", invalidate.get("resourceNames")))
    return NormalizedCachePolicy(
        enabled=presence_from_mapping(raw, "enabled", source_path=source_path),
        read=NormalizedCacheRead(
            enabled=presence_from_mapping(read, "enabled", source_path=f"{source_path}.read"),
            ttl_seconds=_presence_alias(read, ("ttlSeconds", "ttl"), f"{source_path}.read"),
            stale_seconds=_presence_alias(read, ("staleSeconds", "stale"), f"{source_path}.read"),
            scope=presence_from_mapping(read, "scope", source_path=f"{source_path}.read"),
            key_fields=_string_sequence(read.get("keyFields", read.get("keys"))),
            tags=_string_sequence(read.get("tags")),
        ),
        invalidate=NormalizedCacheInvalidation(
            operation_names=operation_names,
            operations=tuple(build_reference(name, kind=ReferenceKind.OPERATION, owner=owner, source_path=f"{source_path}.invalidate.operations.{index}", targets=operation_targets) for index, name in enumerate(operation_names)),
            resource_names=resource_names,
            resources=tuple(build_reference(name, kind=ReferenceKind.RESOURCE, owner=owner, source_path=f"{source_path}.invalidate.resources.{index}", targets=resource_targets) for index, name in enumerate(resource_names)),
            tags=_string_sequence(invalidate.get("tags")),
            all=presence_from_mapping(invalidate, "all", source_path=f"{source_path}.invalidate"),
        ),
        source=source_object(raw, source_path=source_path, known_keys={"enabled", "read", "invalidate"}),
    )


def _transport(raw: Mapping[str, Any]) -> NormalizedRuntimeTransport:
    inbound = _mapping(raw.get("inbound"))
    outbound = _mapping(raw.get("outbound"))
    return NormalizedRuntimeTransport(
        inbound=NormalizedTransportInbound(
            ip=presence_from_mapping(inbound, "ip", source_path="runtime.transport.inbound"),
            user_agent=_presence_alias(inbound, ("userAgent", "user_agent"), "runtime.transport.inbound"),
            headers=freeze_source_map(_mapping(inbound.get("headers"))),
            cookies=freeze_source_map(_mapping(inbound.get("cookies"))),
        ),
        outbound=NormalizedTransportOutbound(
            headers=freeze_source_map(_mapping(outbound.get("headers"))),
            cookies=freeze_source_map(_mapping(outbound.get("cookies"))),
        ),
    )


def _hook_uses(raw: Mapping[str, Any], *, owner: str, source_path: str, resource: str | None, hook_targets: Mapping[str, NormalizedHookDefinition]) -> NormalizedRuntimeHooks:
    return NormalizedRuntimeHooks(
        before_handler=_phase_hooks(raw.get("beforeHandler", raw.get("before_handler")), phase="before_handler", owner=owner, source_path=source_path, resource=resource, hook_targets=hook_targets),
        after_success=_phase_hooks(raw.get("afterSuccess", raw.get("after_success")), phase="after_success", owner=owner, source_path=source_path, resource=resource, hook_targets=hook_targets),
        after_error=_phase_hooks(raw.get("afterError", raw.get("after_error")), phase="after_error", owner=owner, source_path=source_path, resource=resource, hook_targets=hook_targets),
    )


def _phase_hooks(value: Any, *, phase: str, owner: str, source_path: str, resource: str | None, hook_targets: Mapping[str, NormalizedHookDefinition]) -> tuple[NormalizedHookUse, ...]:
    uses: list[NormalizedHookUse] = []
    for index, item in enumerate(_value_sequence(value)):
        raw = _mapping(item)
        ref = item if isinstance(item, str) else raw.get("ref", raw.get("hook"))
        if not isinstance(ref, str) or not ref:
            continue
        qualified = ref if "." in ref or resource is None else f"{resource}.{ref}"
        uses.append(
            NormalizedHookUse(
                ref=ref,
                hook=build_reference(qualified, kind=ReferenceKind.HOOK, owner=owner, source_path=f"{source_path}.{phase}.{index}", targets=hook_targets),
                phase=phase,
                order=_integer(raw.get("order"), default=index),
                source=source_object(raw, source_path=f"{source_path}.{phase}.{index}", known_keys={"ref", "hook", "order"}),
            )
        )
    return tuple(sorted(enumerate(uses), key=lambda pair: (pair[1].order, pair[0]))[index][1] for index in range(len(uses)))


def _data_source(name: str, raw: Mapping[str, Any], *, owner: str, source_path: str, schema_targets: Mapping[str, ApiSchema]) -> NormalizedDataSource:
    return NormalizedDataSource(
        id=name,
        response_field=_optional_text(raw.get("responseField", raw.get("response"))),
        item=_schema_use(raw.get("item", raw.get("itemSchema")), owner=owner, source_path=f"{source_path}.item", schema_targets=schema_targets),
        key_field=_optional_text(raw.get("keyField", raw.get("key"))),
        label_field=_optional_text(raw.get("labelField", raw.get("label"))),
        value_field=_optional_text(raw.get("valueField", raw.get("value"))),
        description=_text(raw.get("description")),
        primary=presence_from_mapping(raw, "primary", source_path=source_path),
        source=source_object(raw, source_path=source_path, known_keys={"responseField", "response", "item", "itemSchema", "keyField", "key", "labelField", "label", "valueField", "value", "description", "primary"}),
    )


def _schema_use(value: Any, *, owner: str, source_path: str, schema_targets: Mapping[str, ApiSchema]) -> SchemaUse[ApiSchema]:
    if isinstance(value, str):
        value = {"$ref": value}
    return build_schema_use(value, owner=owner, source_path=source_path, schema_targets=schema_targets)


def _operation_raw(document: Mapping[str, Any], operation: ApiOperation) -> Mapping[str, Any]:
    path = _mapping(_mapping(document.get("paths")).get(operation.path))
    raw = _mapping(path.get(str(operation.method)))
    return _mapping(raw.get("x-codegen"))


def _presence_alias(raw: Mapping[str, Any], keys: tuple[str, ...], source_path: str) -> PresenceValue[Any]:
    for key in keys:
        if key in raw:
            return PresenceValue.authored(raw[key], source_path=f"{source_path}.{key}")
    return PresenceValue.missing(source_path=f"{source_path}.{keys[0]}")


def _named_items(value: Any) -> tuple[tuple[str, Any], ...]:
    if isinstance(value, Mapping):
        return tuple((str(name), item) for name, item in value.items())
    return tuple((str(_mapping(item).get("name", index)), item) for index, item in enumerate(_sequence(value)))


def _value_sequence(value: Any) -> tuple[Any, ...]:
    if isinstance(value, str | Mapping):
        return (value,)
    return _sequence(value)


def _string_sequence(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in _sequence(value))


def _integer(value: Any, *, default: int) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else default


def _optional_text(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _text(value: Any) -> str:
    return value if isinstance(value, str) and value else "-"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> tuple[Any, ...]:
    return tuple(value) if isinstance(value, list | tuple) else ()


_RESOURCE_KEYS = {"name", "path", "route", "tags", "ui", "access", "accessPolicies", "hooks", "info", "notes"}
_OPERATION_KEYS = {"name", "role", "tags", "ui", "parameters", "target", "query", "params", "body", "response", "sources", "cache", "access", "runtime", "hooks", "info", "notes"}
