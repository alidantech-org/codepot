"""Deterministic template variable contract.

Templates consume this stable contract only. Language adapters fill typed
language/emission/docs models instead of loose dictionaries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Any

from contracts.api import (
    ApiContract,
    ApiEntity,
    ApiEntityConstraint,
    ApiEntityField,
    ApiEntityRelation,
    ApiField,
    ApiOperation,
    ApiParameter,
    ApiRequestBody,
    ApiResource,
    ApiResponse,
    ApiSchema,
)
from contracts.names import NameSet

MetaMap = dict[str, Any]


class TemplateGroup(StrEnum):
    """Stable template groups."""

    GLOBAL = "global"
    RESOURCES = "resources"
    SCHEMAS = "schemas"
    MODELS = "models"
    DTOS = "dtos"
    ENUMS = "enums"
    PRIMITIVES = "primitives"
    ALIASES = "aliases"
    UNKNOWN = "unknown"
    QUERIES = "queries"
    PARAMS = "params"
    BODIES = "bodies"
    RESPONSES = "responses"
    OPERATIONS = "operations"
    FIELDS = "fields"
    FILES = "files"


class TemplateItemKey(StrEnum):
    """Stable item keys used as template roots."""

    RESOURCE = "resource"
    SCHEMA = "schema"
    MODEL = "model"
    DTO = "dto"
    ENUM = "enum"
    PRIMITIVE = "primitive"
    OPERATION = "operation"
    FIELD = "field"
    ENTITY = "entity"
    PARAMETER = "parameter"
    RESPONSE = "response"
    REQUEST = "request"
    FILE = "file"


class TemplateDependencyPurpose(StrEnum):
    """Why one template item depends on another."""

    FIELD_TYPE = "field_type"
    ARRAY_ITEM = "array_item"
    INHERITANCE = "inheritance"
    OPERATION_PARAMETER = "operation_parameter"
    OPERATION_REQUEST_BODY = "operation_request_body"
    OPERATION_RESPONSE = "operation_response"
    OPERATION_TARGET = "operation_target"
    UNKNOWN = "unknown"


class TemplateDependencyTargetKind(StrEnum):
    """Kind of dependency target."""

    PRIMITIVE = "primitive"
    ENUM = "enum"
    MODEL = "model"
    DTO = "dto"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class TemplateDocs:
    """Documentation variables exposed to templates."""

    summary: str = "-"
    description: str = "-"
    deprecated: bool = False
    examples: tuple[Any, ...] = ()


@dataclass(frozen=True)
class TemplateDependencyTarget:
    """Resolved dependency target API/template facts."""

    ref: str
    name: NameSet | None = None
    kind: TemplateDependencyTargetKind = TemplateDependencyTargetKind.UNKNOWN
    schema: ApiSchema | None = None
    is_primitive: bool = False
    is_enum: bool = False
    is_model: bool = False
    is_dto: bool = False


@dataclass(frozen=True)
class TemplateDependency:
    """Dependency visible to templates before/after path resolution."""

    ref: str
    purpose: TemplateDependencyPurpose = TemplateDependencyPurpose.UNKNOWN
    reason: str = "-"
    target: TemplateDependencyTarget | None = None

    is_inheritance: bool = False
    is_importable: bool = False
    is_self: bool = False

    output_path: Path | None = None
    relative_path: Path | None = None
    import_path: str = "-"
    exists: bool = False

    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class TemplateImport:
    """Prepared language-specific import/link visible to templates."""

    ref: str
    label: str = "-"
    path: str = "-"
    statement: str = "-"
    style: str = "-"
    symbols: tuple[str, ...] = ()
    dependency: TemplateDependency | None = None
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class TemplateEnumValue:
    """Enum value with wire value and safe identifier for code generation."""

    wire: str
    name: str
    safe_name: str
    original_name: str = "-"


@dataclass(frozen=True)
class TemplateFile:
    """Current emitted file context injected by emission after path planning."""

    output_path: Path
    relative_path: PurePosixPath
    name: str
    stem: str
    suffix: str
    depth: int = 0
    root_prefix: str = "."
    group: TemplateGroup = TemplateGroup.GLOBAL
    item_key: TemplateItemKey | None = None
    dependencies: tuple[TemplateDependency, ...] = ()
    imports: tuple[TemplateImport, ...] = ()
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class TemplateProjectLang:
    """Project-level language variables."""

    name: str = "-"
    purpose: str = "-"


@dataclass(frozen=True)
class TemplateProjectEmit:
    """Project-level emission variables."""

    format: str = "-"
    root_path: Path | None = None


@dataclass(frozen=True)
class TemplateProject:
    """Project/package-level template variables."""

    name: NameSet
    version: str = "0.1.0"
    description: str = "-"
    lang: TemplateProjectLang = field(default_factory=TemplateProjectLang)
    emit: TemplateProjectEmit = field(default_factory=TemplateProjectEmit)
    docs: TemplateDocs = field(default_factory=TemplateDocs)
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class TemplateFramework:
    """Target framework variables."""

    name: str = "none"
    version: str | None = None
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class TemplatePackage:
    """Target package variables."""

    name: str = "-"
    version: str | None = None
    dependencies: tuple[str, ...] = ()
    dev_dependencies: tuple[str, ...] = ()
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class TemplateFeatures:
    """Target feature flags."""

    text_reports: bool = False
    schema_groups: bool = False
    field_reports: bool = False
    dependency_reports: bool = False
    file_context_reports: bool = False


@dataclass(frozen=True)
class TemplateLanguage:
    """Target language/template profile variables."""

    name: str
    framework: TemplateFramework = field(default_factory=TemplateFramework)
    package: TemplatePackage = field(default_factory=TemplatePackage)
    features: TemplateFeatures = field(default_factory=TemplateFeatures)
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class TemplateEmit:
    """Emission-level template variables."""

    output_path: Path
    template_root: Path | None = None
    dry_run: bool = False
    contract_version: str = "1.0"
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class TemplateItemEmit:
    """Per-item emission variables."""

    group: TemplateGroup
    item_key: TemplateItemKey
    key: str
    ref: str | None = None
    path_parts: tuple[str, ...] = ()
    path: tuple[str, ...] = ()
    resource_path: tuple[str, ...] = ()
    folder_path: tuple[str, ...] = ()
    file_name: str = "-"
    relative_doc_path: tuple[str, ...] = ()
    dependency_refs: tuple[str, ...] = ()
    dependencies: tuple[TemplateDependency, ...] = ()
    imports: tuple[TemplateDependency, ...] = ()


@dataclass(frozen=True)
class TemplateSchemaLang:
    """Schema-level language variables."""

    kind: str = "-"
    type: str = "-"
    display_name: str = "-"
    symbol_name: str = "-"
    field_count: int = 0
    dependency_count: int = 0
    query_enabled: bool = False


@dataclass(frozen=True)
class TemplateFieldLang:
    """Field-level language variables."""

    kind: str = "-"
    type: str = "-"
    display_name: str = "-"
    json_key: str | None = None
    required: bool = False
    nullable: bool = False
    query_enabled: bool = False
    sortable: bool = False
    selectable: bool = False
    filterable: bool = False
    searchable: bool = False
    operators: tuple[str, ...] = ()


@dataclass(frozen=True)
class TemplateOperationLang:
    """Operation-level language variables."""

    kind: str = "-"
    function_name: str = "-"
    display_name: str = "-"
    method: str = "-"
    endpoint_path: str = "-"
    dart_interpolated_endpoint_path: str = "-"
    version: str = "-"


@dataclass(frozen=True)
class TemplateParameterLang:
    """Parameter-level language variables."""

    kind: str = "-"
    display_name: str = "-"
    location: str = "-"
    required: bool = False


@dataclass(frozen=True)
class TemplateRequestBodyLang:
    """Request body language variables."""

    kind: str = "-"
    required: bool = False
    content_types: tuple[str, ...] = ()


@dataclass(frozen=True)
class TemplateResponseLang:
    """Response language variables."""

    kind: str = "-"
    status_code: str = "-"
    is_success: bool = False
    is_error: bool = False
    content_types: tuple[str, ...] = ()


@dataclass(frozen=True)
class TemplateResourceLang:
    """Resource-level language variables."""

    kind: str = "-"
    display_name: str = "-"


@dataclass(frozen=True)
class TemplateFieldMeta:
    """Stable field metadata."""

    default: Any = None
    enum_values: tuple[str, ...] = ()
    enum_options: tuple[TemplateEnumValue, ...] = ()
    enum_type: str | None = None
    enum_ref: str | None = None
    raw_type: str | None = None


@dataclass(frozen=True)
class TemplateSchemaMeta:
    """Stable schema metadata."""

    is_alias: bool = False
    alias_of: str | None = None
    primitive_type: str | None = None
    primitive_format: str | None = None
    enum_type: str | None = None
    enum_values: tuple[str, ...] = ()
    enum_count: int = 0
    composition_refs: tuple[str, ...] = ()
    inherited_refs: tuple[str, ...] = ()
    query_enabled: bool = False
    has_extends: bool = False
    extends_type: str | None = None
    super_fields: tuple[TemplateField, ...] = ()


@dataclass(frozen=True)
class TemplateResourceMeta:
    """Stable resource metadata."""

    operations_count: int = 0
    route: str | None = None
    tags: tuple[str, ...] = ()
    access_ref: str | None = None
    ui: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class TemplateOperationMeta:
    """Stable operation metadata."""

    parameter_count: int = 0
    response_count: int = 0
    has_request_body: bool = False
    request_content_types: tuple[str, ...] = ()
    request_content_type: str | None = None
    is_json_request: bool = False
    is_multipart_request: bool = False
    is_form_url_encoded_request: bool = False
    is_octet_stream_request: bool = False
    is_text_request: bool = False
    target_ref: str | None = None

    query_ref: str | None = None
    query_type: str | None = None
    params_ref: str | None = None
    params_type: str | None = None
    body_ref: str | None = None
    body_type: str | None = None
    response_ref: str | None = None
    response_type: str | None = None
    route_getter: str = "-"
    path_params: tuple[str, ...] = ()
    has_path_params: bool = False
    ui_enabled: bool = False
    ui_role: str | None = None
    ui_inferred: bool = False
    ui_inference_source: str | None = None
    ui_inference_reason: str | None = None
    ui_list_field: str | None = None
    ui_list_item_type: str | None = None
    ui_pagination_field: str | None = None
    ui_sort_fields: tuple[str, ...] = ()
    ui_filter_fields: tuple[str, ...] = ()
    ui_select_fields: tuple[str, ...] = ()
    nest_path: str = "-"
    access_ref: str | None = None
    access_context_ref: str | None = None
    access_context_type: str = "unknown"
    tags: tuple[str, ...] = ()
    cache: MetaMap = field(default_factory=dict)
    source: MetaMap = field(default_factory=dict)
    payload_type: str = "-"
    use_case_interface: str = "-"
    use_case_class: str = "-"
    use_case_impl_class: str = "-"
    use_case_file_name: str = "-"
    use_case_types_file_name: str = "-"
    controller_method_name: str = "-"
    service_method_name: str = "-"


@dataclass(frozen=True)
class TemplateOperationResource:
    """Resource facts attached to an operation for path selectors."""

    name: NameSet
    path: tuple[str, ...] = ()
    route: str | None = None


@dataclass(frozen=True)
class TemplateRequestBodyMeta:
    """Stable request body metadata."""

    ref: str | None = None
    media_type_count: int = 0


@dataclass(frozen=True)
class TemplateResponseMeta:
    """Stable response metadata."""

    ref: str | None = None
    media_type_count: int = 0


@dataclass(frozen=True)
class TemplateParameterMeta:
    """Stable parameter metadata."""

    ref: str | None = None


@dataclass(frozen=True)
class TemplateEntityFieldMeta:
    """Entity field metadata for backend templates."""

    column_name: str = "-"
    column_type: str = "json"
    enum_type: str | None = None
    nullable: bool = False
    primary: bool = False
    generated: str | None = None
    default: Any = None
    min_length: int | None = None
    max_length: int | None = None
    minimum: int | float | None = None
    maximum: int | float | None = None
    exclusive_minimum: bool | int | float | None = None
    exclusive_maximum: bool | int | float | None = None
    multiple_of: int | float | None = None
    pattern: str | None = None
    column_options: str = "-"
    backend_only: bool = False
    raw: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class TemplateEntityField:
    """Entity field template variables."""

    api: ApiEntityField
    name: NameSet
    lang: TemplateFieldLang = field(default_factory=TemplateFieldLang)
    meta: TemplateEntityFieldMeta = field(default_factory=TemplateEntityFieldMeta)


@dataclass(frozen=True)
class TemplateEntityRelation:
    """Entity relation template variables."""

    api: ApiEntityRelation
    name: NameSet
    target_entity_name: str | None = None
    target_class_name: str | None = None
    target_file_name: str | None = None
    inverse_field_name: str | None = None
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class TemplateEntityConstraint:
    """Entity constraint/index template variables."""

    api: ApiEntityConstraint
    name: NameSet
    kind: str = "-"
    fields: tuple[str, ...] = ()
    unique: bool = False
    meta: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class TemplateEntityMeta:
    """Stable entity metadata for backend templates."""

    resource_path: tuple[str, ...] = ()
    resource_name: NameSet | None = None
    schema_type: str | None = None
    store: str | None = None
    table_name: str | None = None
    base_class: str | None = None
    base_import: str | None = None
    interface_type: str | None = None
    class_name: str = "-"
    file_name: str = "-"
    schema_constant: str | None = None
    raw: MetaMap = field(default_factory=dict)


@dataclass(frozen=True)
class TemplateEntity:
    """Entity template variables."""

    api: ApiEntity
    name: NameSet
    resource: TemplateOperationResource | None = None
    fields: tuple[TemplateEntityField, ...] = ()
    backend_fields: tuple[TemplateEntityField, ...] = ()
    relations: tuple[TemplateEntityRelation, ...] = ()
    constraints: tuple[TemplateEntityConstraint, ...] = ()
    emit: TemplateItemEmit | None = None
    docs: TemplateDocs = field(default_factory=TemplateDocs)
    meta: TemplateEntityMeta = field(default_factory=TemplateEntityMeta)


@dataclass(frozen=True)
class TemplateField:
    """Field template variables."""

    api: ApiField
    name: NameSet
    lang: TemplateFieldLang = field(default_factory=TemplateFieldLang)
    emit: TemplateItemEmit | None = None
    docs: TemplateDocs = field(default_factory=TemplateDocs)
    meta: TemplateFieldMeta = field(default_factory=TemplateFieldMeta)


@dataclass(frozen=True)
class TemplateSchema:
    """Schema/model/dto/enum/primitive template variables."""

    api: ApiSchema
    name: NameSet
    fields: tuple[TemplateField, ...] = ()
    lang: TemplateSchemaLang = field(default_factory=TemplateSchemaLang)
    emit: TemplateItemEmit | None = None
    docs: TemplateDocs = field(default_factory=TemplateDocs)
    meta: TemplateSchemaMeta = field(default_factory=TemplateSchemaMeta)


@dataclass(frozen=True)
class TemplateSchemaGroups:
    """Classified template schema views."""

    all: tuple[TemplateSchema, ...] = ()
    models: tuple[TemplateSchema, ...] = ()
    dtos: tuple[TemplateSchema, ...] = ()
    enums: tuple[TemplateSchema, ...] = ()
    primitives: tuple[TemplateSchema, ...] = ()
    aliases: tuple[TemplateSchema, ...] = ()
    unknown: tuple[TemplateSchema, ...] = ()
    queries: tuple[TemplateSchema, ...] = ()
    params: tuple[TemplateSchema, ...] = ()
    bodies: tuple[TemplateSchema, ...] = ()
    responses: tuple[TemplateSchema, ...] = ()
    emit_models: tuple[TemplateSchema, ...] = ()
    emit_dtos: tuple[TemplateSchema, ...] = ()
    emit_enums: tuple[TemplateSchema, ...] = ()


@dataclass(frozen=True)
class TemplateResource:
    """Resource template variables."""

    api: ApiResource
    name: NameSet
    path: tuple[str, ...] = ()
    path_name: NameSet | None = None
    operations: tuple[TemplateOperation, ...] = ()
    models: tuple[TemplateSchema, ...] = ()
    dtos: tuple[TemplateSchema, ...] = ()
    enums: tuple[TemplateSchema, ...] = ()
    schemas: tuple[TemplateSchema, ...] = ()
    entities: tuple[TemplateEntity, ...] = ()
    lang: TemplateResourceLang = field(default_factory=TemplateResourceLang)
    emit: TemplateItemEmit | None = None
    docs: TemplateDocs = field(default_factory=TemplateDocs)
    meta: TemplateResourceMeta = field(default_factory=TemplateResourceMeta)


@dataclass(frozen=True)
class TemplateParameter:
    """Operation parameter template variables."""

    api: ApiParameter
    name: NameSet
    lang: TemplateParameterLang = field(default_factory=TemplateParameterLang)
    emit: TemplateItemEmit | None = None
    docs: TemplateDocs = field(default_factory=TemplateDocs)
    meta: TemplateParameterMeta = field(default_factory=TemplateParameterMeta)


@dataclass(frozen=True)
class TemplateRequestBody:
    """Operation request body template variables."""

    api: ApiRequestBody
    lang: TemplateRequestBodyLang = field(default_factory=TemplateRequestBodyLang)
    emit: TemplateItemEmit | None = None
    docs: TemplateDocs = field(default_factory=TemplateDocs)
    meta: TemplateRequestBodyMeta = field(default_factory=TemplateRequestBodyMeta)


@dataclass(frozen=True)
class TemplateResponse:
    """Operation response template variables."""

    api: ApiResponse
    lang: TemplateResponseLang = field(default_factory=TemplateResponseLang)
    emit: TemplateItemEmit | None = None
    docs: TemplateDocs = field(default_factory=TemplateDocs)
    meta: TemplateResponseMeta = field(default_factory=TemplateResponseMeta)


@dataclass(frozen=True)
class TemplateOperation:
    """Operation template variables."""

    api: ApiOperation
    name: NameSet
    parameters: tuple[TemplateParameter, ...] = ()
    request_body: TemplateRequestBody | None = None
    responses: tuple[TemplateResponse, ...] = ()
    resource: TemplateOperationResource | None = None
    lang: TemplateOperationLang = field(default_factory=TemplateOperationLang)
    emit: TemplateItemEmit | None = None
    docs: TemplateDocs = field(default_factory=TemplateDocs)
    meta: TemplateOperationMeta = field(default_factory=TemplateOperationMeta)


@dataclass(frozen=True)
class TemplateContractMeta:
    """Template contract metadata."""

    debug: bool = False
    schema_count: int = 0
    model_count: int = 0
    dto_count: int = 0
    enum_count: int = 0
    primitive_count: int = 0
    operation_count: int = 0
    resource_count: int = 0


@dataclass(frozen=True)
class TemplateContract:
    """Stable contract passed to emission templates."""

    project: TemplateProject
    api: ApiContract
    lang: TemplateLanguage
    emit: TemplateEmit
    resources: tuple[TemplateResource, ...] = ()
    features: tuple[TemplateResource, ...] = ()
    schemas: TemplateSchemaGroups = field(default_factory=TemplateSchemaGroups)
    operations: tuple[TemplateOperation, ...] = ()
    entities: tuple[TemplateEntity, ...] = ()
    file: TemplateFile | None = None
    meta: TemplateContractMeta = field(default_factory=TemplateContractMeta)
