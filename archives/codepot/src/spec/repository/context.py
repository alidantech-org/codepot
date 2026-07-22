"""Spec repository context builder."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar

from archives.codepot.src.contracts.spec.context import SpecContext, SpecMetadata
from archives.codepot.src.contracts.spec.records import SpecRecord, SpecRecordSet
from archives.codepot.src.spec.ir.properties.composite.definition import CompositeDefinition
from archives.codepot.src.spec.ir.properties.enum.definition import EnumDefinition
from archives.codepot.src.spec.ir.properties.primitive.definition import PrimitiveDefinition
from archives.codepot.src.spec.ir.resource.definition import ResourceDefinition
from archives.codepot.src.spec.ir.resource.operation.definition import OperationDefinition
from archives.codepot.src.spec.ir.resource.route.definition import RouteMethodDefinition, RoutePathDefinition
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
from archives.codepot.src.spec.ir.shared.document import CodepotDefinition
from archives.codepot.src.spec.ir.shared.url import UrlDefinition
from archives.codepot.src.spec.repository.counts import build_counts
from archives.codepot.src.spec.repository.metadata import build_metadata
from archives.codepot.src.spec.repository.owner_index import OwnerFolderIndex, build_owner_folder_index
from archives.codepot.src.spec.repository.ownership import create_owner_from_identity
from archives.codepot.src.spec.repository.records import create_spec_record
from archives.codepot.src.spec.repository.subjects import subject_to_record_kind
from archives.codepot.src.spec.utils.enums import SpecSubject


@dataclass(frozen=True)
class RepositoryRecords:
    """All normalized repository records grouped by typed subject."""

    urls: tuple[SpecRecord[UrlDefinition], ...]
    content_types: tuple[SpecRecord[ContentTypeDefinition], ...]

    primitives: tuple[SpecRecord[PrimitiveDefinition], ...]
    enums: tuple[SpecRecord[EnumDefinition], ...]
    composites: tuple[SpecRecord[CompositeDefinition], ...]

    entities: tuple[SpecRecord[EntityDefinition], ...]
    field_sets: tuple[SpecRecord[FieldSetDefinition], ...]
    models: tuple[SpecRecord[ModelDefinition], ...]
    dtos: tuple[SpecRecord[DtoDefinition], ...]
    params: tuple[SpecRecord[ParamsDefinition], ...]

    resources: tuple[SpecRecord[ResourceDefinition], ...]
    operations: tuple[SpecRecord[OperationDefinition], ...]
    route_paths: tuple[SpecRecord[RoutePathDefinition], ...]
    routes: tuple[SpecRecord[RouteMethodDefinition], ...]

    errors: tuple[SpecRecord[ErrorResponseDefinition], ...]

    security_credentials: tuple[SpecRecord[SecurityCredentialDefinition], ...]
    security_principals: tuple[SpecRecord[SecurityPrincipalDefinition], ...]
    security_policies: tuple[SpecRecord[SecurityPolicyDefinition], ...]


TData = TypeVar("TData")


def _records_from_map(
    subject: SpecSubject,
    values: dict[str, TData],
    owner_index: OwnerFolderIndex,
) -> tuple[SpecRecord[TData], ...]:
    """Create normalized records from a typed IR map."""

    return tuple(
        create_spec_record(
            subject=subject,
            key=key,
            data=value,
            owner=create_owner_from_identity(
                key=key,
                owner_index=owner_index,
            ),
        )
        for key, value in values.items()
    )


def _records_from_list(
    subject: SpecSubject,
    values: list[TData],
) -> tuple[SpecRecord[TData], ...]:
    """Create normalized records from a typed IR list."""

    return tuple(
        create_spec_record(
            subject=subject,
            key=str(index),
            data=value,
        )
        for index, value in enumerate(values)
    )


def _record_set(
    subject: SpecSubject,
    items: tuple[SpecRecord[TData], ...],
) -> SpecRecordSet[TData]:
    """Create a typed record set."""

    return SpecRecordSet(
        kind=subject_to_record_kind(subject),
        items=items,
    )


def _resource_operations(
    resources: dict[str, ResourceDefinition],
    owner_index: OwnerFolderIndex,
) -> tuple[SpecRecord[OperationDefinition], ...]:
    """Create operation records from typed resources."""

    records: list[SpecRecord[OperationDefinition]] = []

    for resource_key, resource in resources.items():
        for operation_key, operation in resource.operations.items():
            key = f"{resource_key}.{operation_key}"
            owner = create_owner_from_identity(
                key=f"resource.{resource_key}.{operation_key}",
                owner_index=owner_index,
            )
            records.append(
                create_spec_record(
                    subject=SpecSubject.OPERATIONS,
                    key=key,
                    data=operation,
                    owner=owner,
                )
            )

    return tuple(records)


def _resource_route_paths(
    resources: dict[str, ResourceDefinition],
    owner_index: OwnerFolderIndex,
) -> tuple[SpecRecord[RoutePathDefinition], ...]:
    """Create route path records from typed resources."""

    records: list[SpecRecord[RoutePathDefinition]] = []

    for resource_key, resource in resources.items():
        for route_path_key, route_path in resource.routes.items():
            key = f"{resource_key}.{route_path_key}"
            owner = create_owner_from_identity(
                key=f"resource.{resource_key}.{route_path_key}",
                owner_index=owner_index,
            )
            records.append(
                create_spec_record(
                    subject=SpecSubject.ROUTE_PATHS,
                    key=key,
                    data=route_path,
                    owner=owner,
                )
            )

    return tuple(records)


def _resource_routes(
    resources: dict[str, ResourceDefinition],
    owner_index: OwnerFolderIndex,
) -> tuple[SpecRecord[RouteMethodDefinition], ...]:
    """Create route method records from typed resources."""

    records: list[SpecRecord[RouteMethodDefinition]] = []

    for resource_key, resource in resources.items():
        for route_path_key, route_path in resource.routes.items():
            for method, route_method in route_path.methods.items():
                key = f"{resource_key}.{route_path_key}.{method}"
                owner = create_owner_from_identity(
                    key=f"resource.{resource_key}.{method}",
                    owner_index=owner_index,
                )
                records.append(
                    create_spec_record(
                        subject=SpecSubject.ROUTES,
                        key=key,
                        data=route_method,
                        owner=owner,
                    )
                )

    return tuple(records)


def build_repository_records(document: CodepotDefinition) -> RepositoryRecords:
    """Build all normalized repository records from a typed document."""

    owner_index = build_owner_folder_index(
        resources=document.resources,
        entities=document.schemas.entities,
    )

    return RepositoryRecords(
        urls=_records_from_list(SpecSubject.URLS, document.urls),
        content_types=_records_from_map(
            SpecSubject.CONTENT_TYPES,
            document.content_types,
            owner_index,
        ),
        primitives=_records_from_map(
            SpecSubject.PRIMITIVES,
            document.properties.primitives,
            owner_index,
        ),
        enums=_records_from_map(SpecSubject.ENUMS, document.properties.enums, owner_index),
        composites=_records_from_map(
            SpecSubject.COMPOSITES,
            document.properties.composites,
            owner_index,
        ),
        entities=_records_from_map(SpecSubject.ENTITIES, document.schemas.entities, owner_index),
        field_sets=_records_from_map(
            SpecSubject.FIELD_SETS,
            document.schemas.field_sets,
            owner_index,
        ),
        models=_records_from_map(SpecSubject.MODELS, document.schemas.models, owner_index),
        dtos=_records_from_map(SpecSubject.DTOS, document.schemas.dtos, owner_index),
        params=_records_from_map(SpecSubject.PARAMS, document.schemas.params, owner_index),
        resources=_records_from_map(SpecSubject.RESOURCES, document.resources, owner_index),
        operations=_resource_operations(document.resources, owner_index),
        route_paths=_resource_route_paths(document.resources, owner_index),
        routes=_resource_routes(document.resources, owner_index),
        errors=_records_from_map(SpecSubject.ERRORS, document.responses.errors, owner_index),
        security_credentials=_records_from_map(
            SpecSubject.SECURITY_CREDENTIALS,
            document.security.credentials,
            owner_index,
        ),
        security_principals=_records_from_map(
            SpecSubject.SECURITY_PRINCIPALS,
            document.security.principals,
            owner_index,
        ),
        security_policies=_records_from_map(
            SpecSubject.SECURITY_POLICIES,
            document.security.policies,
            owner_index,
        ),
    )


def records_by_subject(
    records: RepositoryRecords,
) -> dict[SpecSubject, tuple[SpecRecord[object], ...]]:
    """Return repository records keyed by subject."""

    return {
        SpecSubject.URLS: records.urls,
        SpecSubject.CONTENT_TYPES: records.content_types,
        SpecSubject.PRIMITIVES: records.primitives,
        SpecSubject.ENUMS: records.enums,
        SpecSubject.COMPOSITES: records.composites,
        SpecSubject.ENTITIES: records.entities,
        SpecSubject.FIELD_SETS: records.field_sets,
        SpecSubject.MODELS: records.models,
        SpecSubject.DTOS: records.dtos,
        SpecSubject.PARAMS: records.params,
        SpecSubject.RESOURCES: records.resources,
        SpecSubject.OPERATIONS: records.operations,
        SpecSubject.ROUTE_PATHS: records.route_paths,
        SpecSubject.ROUTES: records.routes,
        SpecSubject.ERRORS: records.errors,
        SpecSubject.SECURITY_CREDENTIALS: records.security_credentials,
        SpecSubject.SECURITY_PRINCIPALS: records.security_principals,
        SpecSubject.SECURITY_POLICIES: records.security_policies,
    }


def all_records(records: RepositoryRecords) -> tuple[SpecRecord[object], ...]:
    """Flatten all repository records."""

    grouped = records_by_subject(records)
    return tuple(
        record for subject_records in grouped.values() for record in subject_records
    )


def build_context(path: Path, document: CodepotDefinition) -> SpecContext:
    """Build complete normalized spec context."""

    metadata: SpecMetadata = build_metadata(path, document)
    records = build_repository_records(document)
    by_subject = records_by_subject(records)
    counts = build_counts(by_subject)

    return SpecContext(
        metadata=metadata,
        counts=counts,
        urls=_record_set(SpecSubject.URLS, records.urls),
        content_types=_record_set(
            SpecSubject.CONTENT_TYPES,
            records.content_types,
        ),
        primitives=_record_set(SpecSubject.PRIMITIVES, records.primitives),
        enums=_record_set(SpecSubject.ENUMS, records.enums),
        composites=_record_set(SpecSubject.COMPOSITES, records.composites),
        entities=_record_set(SpecSubject.ENTITIES, records.entities),
        field_sets=_record_set(SpecSubject.FIELD_SETS, records.field_sets),
        models=_record_set(SpecSubject.MODELS, records.models),
        dtos=_record_set(SpecSubject.DTOS, records.dtos),
        params=_record_set(SpecSubject.PARAMS, records.params),
        resources=_record_set(SpecSubject.RESOURCES, records.resources),
        operations=_record_set(SpecSubject.OPERATIONS, records.operations),
        route_paths=_record_set(SpecSubject.ROUTE_PATHS, records.route_paths),
        routes=_record_set(SpecSubject.ROUTES, records.routes),
        errors=_record_set(SpecSubject.ERRORS, records.errors),
        security_credentials=_record_set(
            SpecSubject.SECURITY_CREDENTIALS,
            records.security_credentials,
        ),
        security_principals=_record_set(
            SpecSubject.SECURITY_PRINCIPALS,
            records.security_principals,
        ),
        security_policies=_record_set(
            SpecSubject.SECURITY_POLICIES,
            records.security_policies,
        ),
        all_records=all_records(records),
    )
