"""Lossless enrichment for the stable inference-to-API contract boundary."""

from __future__ import annotations

from dataclasses import replace

from contracts.api import ApiContract
from contracts.normalized import contract_collection
from contracts.normalized_api import build_normalized_api_view
from contracts.normalized_codegen_contract import build_normalized_codegen_contract
from contracts.normalized_domains import build_normalized_domain_view
from contracts.normalized_entity_contract import build_normalized_entity_contract
from contracts.normalized_frontend_contract import build_normalized_frontend_contract
from contracts.normalized_schema_contract import build_normalized_schema_contract
from contracts.normalized_sources import extend_normalized_source_registry
from contracts.source import freeze_source_map
from inference.contract import build_api_contract as build_compatibility_api_contract
from inference.models import InferenceGraph


def build_api_contract(graph: InferenceGraph) -> ApiContract:
    """Build the established API contract and attach additive lossless views."""

    contract = build_compatibility_api_contract(graph)
    raw = graph.raw or {}
    extensions = {
        str(key): value
        for key, value in raw.items()
        if isinstance(key, str) and key.startswith("x-")
    }
    normalized = extend_normalized_source_registry(
        build_normalized_api_view(contract, raw),
        raw,
    )
    domains = build_normalized_domain_view(contract, raw)
    schema_contract = build_normalized_schema_contract(contract, raw)
    entity_contract = build_normalized_entity_contract(contract, raw)
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
            "normalized": normalized,
            "normalized_domains": domains,
            "normalized_schemas": schema_contract,
            "normalized_codegen": codegen_contract,
            "normalized_entities": entity_contract,
            "normalized_frontends": frontend_contract,
            "loss_count": normalized.loss_count + schema_contract.loss_count,
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
