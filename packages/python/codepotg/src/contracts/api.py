"""Language-neutral API contract.

This module defines stable inferred API facts that language adapters consume.
It must not contain Dart, TypeScript, template, emission, or CLI behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from archives.codepotg.src.contracts.names import NameSet
from archives.codepotg.src.contracts.source import FrozenMap

MetaMap = dict[str, Any]


class ApiSchemaKind(StrEnum):
    """Stable API schema kinds."""

    UNKNOWN = "unknown"
    ENUM = "enum"
    MODEL = "model"
    DTO = "dto"
    PRIMITIVE = "primitive"


class ApiFieldKind(StrEnum):
    """Stable resolved field kinds."""

    UNKNOWN = "unknown"
    PRIMITIVE = "primitive"
    ENUM = "enum"
    MODEL = "model"
    DTO = "dto"
    ARRAY = "array"
    OBJECT = "object"


class ApiHttpMethod(StrEnum):
    """Stable HTTP method values."""

    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"
    OPTIONS = "options"
    HEAD = "head"
    TRACE = "trace"
    UNKNOWN = "unknown"


class ApiOperationRole(StrEnum):
    """Stable operation/schema role values."""

    UNKNOWN = "unknown"
    QUERY = "query"
    PARAMS = "params"
    BODY = "body"
    REQUEST = "request"
    RESPONSE = "response"


@dataclass(frozen=True)
class ApiDocumentInfo:
    """Top-level API document information."""

    title: str = "-"
    openapi_version: str = "-"
    api_version: str = "-"
    description: str = "-"


@dataclass(frozen=True)
class ApiServer:
    """OpenAPI server information."""

    url: str
    description: str = "-"
    variables: MetaMap = field(default_factory=dict)
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class ApiQueryOptions:
    """Query behavior inferred from x-codegen.query."""

    filterable: bool = False
    operators: tuple[str, ...] = ()
    sortable: bool = False
    selectable: bool = False
    searchable: bool = False
    meta: MetaMap = field(default_factory=dict)

    @property
    def enabled(self) -> bool:
        """Return whether any query behavior is enabled."""
        return bool(self.filterable or self.operators or self.sortable or self.selectable or self.searchable)  # noqa: E501


@dataclass(frozen=True)
class ApiResource:
    """Inferred resource group."""

    id: str
    name: NameSet
    path: tuple[str, ...] = ()
    path_name: NameSet | None = None
    operations_count: int = 0
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class ApiFieldType:
    """Resolved field type facts."""

    raw_type: str | None = None
    format: str | None = None
    kind: ApiFieldKind = ApiFieldKind.UNKNOWN
    type: str | None = None
    resolved_format: str | None = None
    item_kind: ApiFieldKind = ApiFieldKind.UNKNOWN
    item_type: str | None = None
    item_format: str | None = None


@dataclass(frozen=True)
class ApiEntityField:
    """Language-neutral entity field fact from x-codegen.entities."""

    id: str
    name: NameSet
    schema_ref: str | None = None
    required: bool = True
    nullable: bool = False
    type: ApiFieldType = field(default_factory=ApiFieldType)
    default: Any = None
    min_length: int | None = None
    max_length: int | None = None
    minimum: int | float | None = None
    maximum: int | float | None = None
    exclusive_minimum: bool | int | float | None = None
    exclusive_maximum: bool | int | float | None = None
    multiple_of: int | float | None = None
    pattern: str | None = None
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class ApiEntityRelation:
    """Language-neutral entity relation fact."""

    id: str
    name: NameSet
    cardinality: str = "-"
    target_ref: str | None = None
    local: str | None = None
    foreign: str | None = None
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class ApiEntityConstraint:
    """Language-neutral entity constraint/index fact."""

    id: str
    name: NameSet
    kind: str = "-"
    fields: tuple[str, ...] = ()
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class ApiEntity:
    """Entity fact from root x-codegen.entities."""

    id: str
    name: NameSet
    resource: str | None = None
    resource_ref: str | None = None
    schema_ref: str | None = None
    store: str | None = None
    extends: MetaMap = field(default_factory=dict)
    fields: tuple[ApiEntityField, ...] = ()
    backend_fields: tuple[ApiEntityField, ...] = ()
    relations: tuple[ApiEntityRelation, ...] = ()
    constraints: tuple[ApiEntityConstraint, ...] = ()
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class ApiField:
    """Language-neutral schema field fact."""

    id: str
    name: NameSet
    required: bool = True
    nullable: bool = False
    type: ApiFieldType = field(default_factory=ApiFieldType)
    schema_ref: str | None = None
    schema_refs: tuple[str, ...] = ()
    item_ref: str | None = None
    item_refs: tuple[str, ...] = ()
    enum_values: tuple[str, ...] = ()
    default: Any = None
    min_length: int | None = None
    max_length: int | None = None
    minimum: int | float | None = None
    maximum: int | float | None = None
    exclusive_minimum: bool | int | float | None = None
    exclusive_maximum: bool | int | float | None = None
    multiple_of: int | float | None = None
    pattern: str | None = None
    description: str = "-"
    query: ApiQueryOptions = field(default_factory=ApiQueryOptions)
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class ApiEnumValue:
    """Language-neutral enum value fact."""

    value: str
    name: NameSet
    description: str = "-"
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class ApiComposition:
    """Schema composition facts."""

    kind: str
    refs: tuple[str, ...] = ()
    inline_field_count: int = 0


@dataclass(frozen=True)
class ApiSchema:
    """Language-neutral schema fact."""

    id: str
    name: NameSet
    ref: str
    kind: ApiSchemaKind
    resource: str | None = None

    dependencies: tuple[str, ...] = ()
    is_alias: bool = False
    alias_of: str | None = None
    nullable: bool = False

    primitive_type: str | None = None
    primitive_format: str | None = None
    query: ApiQueryOptions = field(default_factory=ApiQueryOptions)

    enum_type: str | None = None
    enum_values: tuple[ApiEnumValue, ...] = ()

    fields: tuple[ApiField, ...] = ()
    composition_refs: tuple[str, ...] = ()
    inherited_refs: tuple[str, ...] = ()
    composition: ApiComposition | None = None
    has_field_overrides: bool = False

    description: str = "-"
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class ApiSchemaGroups:
    """Classified schema views."""

    all: tuple[ApiSchema, ...] = ()
    models: tuple[ApiSchema, ...] = ()
    dtos: tuple[ApiSchema, ...] = ()
    enums: tuple[ApiSchema, ...] = ()
    primitives: tuple[ApiSchema, ...] = ()
    aliases: tuple[ApiSchema, ...] = ()
    unknown: tuple[ApiSchema, ...] = ()

    queries: tuple[ApiSchema, ...] = ()
    params: tuple[ApiSchema, ...] = ()
    bodies: tuple[ApiSchema, ...] = ()
    responses: tuple[ApiSchema, ...] = ()

    emit_models: tuple[ApiSchema, ...] = ()
    emit_dtos: tuple[ApiSchema, ...] = ()
    emit_enums: tuple[ApiSchema, ...] = ()


@dataclass(frozen=True)
class ApiMediaType:
    """Operation media type fact."""

    content_type: str
    schema_ref: str | None = None
    schema_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class ApiParameter:
    """Language-neutral operation parameter fact."""

    id: str
    name: NameSet
    location: str
    required: bool = False
    ref: str | None = None
    schema_ref: str | None = None
    schema_refs: tuple[str, ...] = ()
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class ApiRequestBody:
    """Language-neutral request body fact."""

    ref: str | None = None
    required: bool = False
    content_types: tuple[str, ...] = ()
    media_types: tuple[ApiMediaType, ...] = ()
    schema_refs: tuple[str, ...] = ()
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class ApiResponse:
    """Language-neutral operation response fact."""

    status_code: str
    ref: str | None = None
    description: str = "-"
    content_types: tuple[str, ...] = ()
    media_types: tuple[ApiMediaType, ...] = ()
    schema_refs: tuple[str, ...] = ()
    is_success: bool = False
    is_error: bool = False
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class ApiOperationTarget:
    """Operation target metadata from inference."""

    ref: str
    source: str
    exclude: tuple[str, ...] = ()
    inferred_roles: tuple[str, ...] = ()
    locations: tuple[str, ...] = ()
    reason: str = ""


@dataclass(frozen=True)
class ApiOperation:
    """Language-neutral operation fact."""

    id: str
    name: NameSet
    method: ApiHttpMethod
    path: str
    resource: str | None = None
    parameters: tuple[ApiParameter, ...] = ()
    request_body: ApiRequestBody | None = None
    responses: tuple[ApiResponse, ...] = ()
    target: ApiOperationTarget | None = None
    description: str = "-"
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class ApiDependency:
    """Dependency between schema refs."""

    source_ref: str
    target_ref: str


@dataclass(frozen=True)
class ApiContract:
    """Stable API contract produced from inference."""

    info: ApiDocumentInfo
    resources: tuple[ApiResource, ...] = ()
    servers: tuple[ApiServer, ...] = ()
    schemas: ApiSchemaGroups = field(default_factory=ApiSchemaGroups)
    operations: tuple[ApiOperation, ...] = ()
    entities: tuple[ApiEntity, ...] = ()
    dependencies: tuple[ApiDependency, ...] = ()
    meta: MetaMap = field(default_factory=dict)
    raw: FrozenMap = field(default_factory=FrozenMap)
    extensions: FrozenMap = field(default_factory=FrozenMap)
