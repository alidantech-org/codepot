"""Lossless enrichment for the stable inference-to-API contract boundary."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from typing import Any

from archives.codepotg.src.contracts.api import (
    ApiContract,
    ApiEntity,
    ApiEntityConstraint,
    ApiEntityField,
    ApiEntityRelation,
    ApiFieldType,
)
from archives.codepotg.src.contracts.names import make_contract_name
from archives.codepotg.src.contracts.normalized import contract_collection
from archives.codepotg.src.contracts.normalized_api import build_normalized_api_view
from archives.codepotg.src.contracts.normalized_codegen_contract import build_normalized_codegen_contract
from archives.codepotg.src.contracts.normalized_document_contract import build_normalized_document_contract
from archives.codepotg.src.contracts.normalized_domains import build_normalized_domain_view
from archives.codepotg.src.contracts.normalized_entity_contract import (
    NormalizedEntityContract,
    NormalizedEntityContractView,
    NormalizedEntityFieldContract,
    build_normalized_entity_contract,
)
from archives.codepotg.src.contracts.normalized_frontend_contract import build_normalized_frontend_contract
from archives.codepotg.src.contracts.normalized_schema_contract import build_normalized_schema_contract
from archives.codepotg.src.contracts.normalized_sources import extend_normalized_source_registry
from archives.codepotg.src.contracts.source import freeze_source_map
from archives.codepotg.src.inference.contract import build_api_contract as build_compatibility_api_contract
from archives.codepotg.src.inference.models import InferenceGraph


def build_api_contract(graph: InferenceGraph) -> ApiContract:
    """Build the established API contract and attach additive lossless views."""

    contract = build_compatibility_api_contract(graph)
    raw = graph.raw or {}
    extensions = {
        str(key): value
        for key, value in raw.items()
        if isinstance(key, str) and key.startswith("x-")
    }

    entity_contract = build_normalized_entity_contract(contract, raw)
    if _uses_flat_entity_shape(raw):
        contract = replace(
            contract,
            entities=_compatibility_entities(entity_contract),
        )

    document_contract = build_normalized_document_contract(raw)
    normalized = extend_normalized_source_registry(
        build_normalized_api_view(contract, raw),
        raw,
    )
    domains = build_normalized_domain_view(contract, raw)
    schema_contract = build_normalized_schema_contract(contract, raw)
    codegen_contract = build_normalized_codegen_contract(contract, raw, domains)
    codegen_contract = replace(
        codegen_contract,
        resources=contract_collection(
            replace(
                resource,
                entities=contract_collection(
                    entity
                    for entity in entity_contract.entities.all
                    if entity.resource is not None
                    and entity.resource.is_resolved
                    and entity.resource.target is not None
                    and entity.resource.target.id == resource.id
                ),
            )
            for resource in codegen_contract.resources.all
        ),
    )
    frontend_contract = build_normalized_frontend_contract(contract, raw)

    return replace(
        contract,
        raw=freeze_source_map(raw),
        extensions=freeze_source_map(extensions),
        meta={
            **contract.meta,
            "normalized_document": document_contract,
            "normalized": normalized,
            "normalized_domains": domains,
            "normalized_schemas": schema_contract,
            "normalized_codegen": codegen_contract,
            "normalized_entities": entity_contract,
            "normalized_frontends": frontend_contract,
            "loss_count": (
                document_contract.loss_count
                + normalized.loss_count
                + schema_contract.loss_count
            ),
            "unresolved_count": (
                normalized.unresolved_count
                + domains.unresolved_count
                + schema_contract.unresolved_count
                + codegen_contract.unresolved_count
                + entity_contract.unresolved_count
                + frontend_contract.unresolved_count
            ),
            "cycle_count": entity_contract.cycle_count,
            "raw_only_count": normalized.raw_only_count,
        },
    )


def _uses_flat_entity_shape(raw: Mapping[str, Any]) -> bool:
    codegen = _mapping(raw.get("x-codegen"))
    entities = _mapping(codegen.get("entities"))
    return any(
        isinstance(value, Mapping)
        and bool(_FLAT_ENTITY_KEYS.intersection(value))
        for value in entities.values()
    )


def _compatibility_entities(
    contract: NormalizedEntityContract,
) -> tuple[ApiEntity, ...]:
    return tuple(_compatibility_entity(entity) for entity in contract.entities.all)


def _compatibility_entity(entity: NormalizedEntityContractView) -> ApiEntity:
    resource = entity.resource.ref if entity.resource is not None else None
    schema_ref = entity.schema.ref.ref if entity.schema.ref is not None else None
    identifier = f"{resource}.{entity.id}" if resource else entity.id
    return ApiEntity(
        id=identifier,
        name=make_contract_name(entity.id),
        resource=resource,
        resource_ref=resource,
        schema_ref=schema_ref,
        store=entity.store,
        extends={
            "refs": tuple(reference.ref for reference in entity.extends),
        },
        fields=tuple(
            _compatibility_field(field)
            for field in entity.declared_fields.all
        ),
        backend_fields=tuple(
            _compatibility_field(field)
            for field in entity.backend_fields.all
        ),
        relations=tuple(
            ApiEntityRelation(
                id=relation.id,
                name=make_contract_name(relation.id),
                cardinality=relation.cardinality,
                target_ref=(
                    relation.target.ref
                    if relation.target is not None
                    else None
                ),
                local=(relation.local_fields[0] if relation.local_fields else None),
                foreign=(
                    relation.foreign_fields[0]
                    if relation.foreign_fields
                    else None
                ),
                meta={
                    "local_fields": relation.local_fields,
                    "foreign_fields": relation.foreign_fields,
                    "normalized": relation,
                },
            )
            for relation in entity.relations.all
        ),
        constraints=tuple(
            ApiEntityConstraint(
                id=constraint.id,
                name=make_contract_name(constraint.id),
                kind=constraint.kind,
                fields=constraint.fields,
                meta={"normalized": constraint},
            )
            for constraint in entity.constraints.all
        ),
        meta={"normalized": entity},
    )


def _compatibility_field(
    field: NormalizedEntityFieldContract,
) -> ApiEntityField:
    raw_type = field.type.value if isinstance(field.type.value, str) else None
    return ApiEntityField(
        id=field.id,
        name=make_contract_name(field.id),
        schema_ref=(
            field.schema_use.ref.ref
            if field.schema_use.ref is not None
            else None
        ),
        nullable=field.constraints.get("nullable") is True,
        type=ApiFieldType(raw_type=raw_type, type=raw_type),
        default=field.default.value if field.default.is_set else None,
        min_length=_integer(field.constraints.get("minLength")),
        max_length=_integer(field.constraints.get("maxLength")),
        minimum=_number(field.constraints.get("minimum")),
        maximum=_number(field.constraints.get("maximum")),
        exclusive_minimum=field.constraints.get("exclusiveMinimum"),
        exclusive_maximum=field.constraints.get("exclusiveMaximum"),
        multiple_of=_number(field.constraints.get("multipleOf")),
        pattern=_text(field.constraints.get("pattern")),
        meta={"normalized": field},
    )


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _integer(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _number(value: Any) -> int | float | None:
    return value if isinstance(value, int | float) and not isinstance(value, bool) else None


def _text(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


_FLAT_ENTITY_KEYS = {
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
