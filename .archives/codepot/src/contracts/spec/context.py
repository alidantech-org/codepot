"""Complete normalized spec context contract."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from archives.codepot.src.contracts.spec.records import SpecRecord, SpecRecordSet
from archives.codepot.src.spec.ir.properties.composite.definition import CompositeDefinition
from archives.codepot.src.spec.ir.properties.enum.definition import EnumDefinition
from archives.codepot.src.spec.ir.properties.primitive.definition import PrimitiveDefinition
from archives.codepot.src.spec.ir.resource.definition import ResourceDefinition
from archives.codepot.src.spec.ir.resource.operation.definition import OperationDefinition
from archives.codepot.src.spec.ir.resource.route.definition import (
    RouteMethodDefinition,
    RoutePathDefinition,
)
from archives.codepot.src.spec.ir.response.errors.definition import ErrorResponseDefinition
from archives.codepot.src.spec.ir.schema.dto.definition import DtoDefinition
from archives.codepot.src.spec.ir.schema.entity.definition import EntityDefinition
from archives.codepot.src.spec.ir.schema.field_set.definition import FieldSetDefinition
from archives.codepot.src.spec.ir.schema.model.definition import ModelDefinition
from archives.codepot.src.spec.ir.schema.params.definition import ParamsDefinition
from archives.codepot.src.spec.ir.security.definition import (
    SecurityCredentialDefinition,
    SecurityPolicyDefinition,
    SecurityPrincipalDefinition,
)
from archives.codepot.src.spec.ir.shared.content import ContentTypeDefinition
from archives.codepot.src.spec.ir.shared.url import UrlDefinition


@dataclass(frozen=True)
class SpecFileMetadata:
    """Source file metadata for the loaded compiled spec."""

    path: Path
    size_bytes: int
    size_label: str
    line_count: int
    hash: str


@dataclass(frozen=True)
class SpecProjectMetadata:
    """Project/API metadata from the compiled spec root."""

    codepot_version: str
    project_key: str
    version: int
    title: str
    project_version: str | None
    summary: str | None
    terms_of_service: str | None


@dataclass(frozen=True)
class SpecContactMetadata:
    """Normalized API contact metadata."""

    name: str | None
    url: str | None
    email: str | None


@dataclass(frozen=True)
class SpecLicenseMetadata:
    """Normalized API license metadata."""

    name: str
    identifier: str | None
    url: str | None


@dataclass(frozen=True)
class SpecInfoLinksMetadata:
    """Normalized project information links."""

    website: str | None
    docs: str | None
    support: str | None
    changelog: str | None
    status: str | None
    repository: str | None


@dataclass(frozen=True)
class SpecMetadata:
    """Complete normalized metadata for a compiled spec."""

    file: SpecFileMetadata
    project: SpecProjectMetadata
    contact: SpecContactMetadata | None
    license: SpecLicenseMetadata | None
    links: SpecInfoLinksMetadata | None


@dataclass(frozen=True)
class SpecCounts:
    """Precomputed counts from the normalized spec repository."""

    urls: int
    content_types: int

    primitives: int
    enums: int
    composites: int

    entities: int
    field_sets: int
    models: int
    dtos: int
    params: int

    resources: int
    operations: int
    route_paths: int
    routes: int

    errors: int

    security_credentials: int
    security_principals: int
    security_policies: int

    properties_total: int
    schemas_total: int
    security_total: int
    records_total: int


@dataclass(frozen=True)
class SpecContext:
    """Complete normalized spec context exposed by the spec repository.

    The collections are record sets wrapping original typed IR objects. This
    keeps the IR as the data source of truth while making iteration, naming,
    ownership, refs, and dependencies consistent for codegen.
    """

    metadata: SpecMetadata
    counts: SpecCounts

    urls: SpecRecordSet[UrlDefinition]
    content_types: SpecRecordSet[ContentTypeDefinition]

    primitives: SpecRecordSet[PrimitiveDefinition]
    enums: SpecRecordSet[EnumDefinition]
    composites: SpecRecordSet[CompositeDefinition]

    entities: SpecRecordSet[EntityDefinition]
    field_sets: SpecRecordSet[FieldSetDefinition]
    models: SpecRecordSet[ModelDefinition]
    dtos: SpecRecordSet[DtoDefinition]
    params: SpecRecordSet[ParamsDefinition]

    resources: SpecRecordSet[ResourceDefinition]
    operations: SpecRecordSet[OperationDefinition]
    route_paths: SpecRecordSet[RoutePathDefinition]
    routes: SpecRecordSet[RouteMethodDefinition]

    errors: SpecRecordSet[ErrorResponseDefinition]

    security_credentials: SpecRecordSet[SecurityCredentialDefinition]
    security_principals: SpecRecordSet[SecurityPrincipalDefinition]
    security_policies: SpecRecordSet[SecurityPolicyDefinition]

    all_records: tuple[SpecRecord[object], ...]
