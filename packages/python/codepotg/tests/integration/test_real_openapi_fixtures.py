from __future__ import annotations

from tests.fixtures.openapi import load_real_contract


def test_real_json_and_yaml_fixtures_produce_the_same_contract(
    real_openapi_json_path,
    real_openapi_yaml_path,
) -> None:
    json_contract = load_real_contract(real_openapi_json_path)
    yaml_contract = load_real_contract(real_openapi_yaml_path)

    assert _contract_signature(json_contract) == _contract_signature(yaml_contract)


def test_real_fixture_exercises_the_full_codegen_contract(
    real_openapi_yaml_path,
) -> None:
    contract = load_real_contract(real_openapi_yaml_path)
    normalized_entities = contract.meta["normalized_entities"]
    normalized_frontends = contract.meta["normalized_frontends"]
    normalized_codegen = contract.meta["normalized_codegen"]

    assert contract.info.title == "Alidantech API"
    assert len(contract.resources) >= 10
    assert len(contract.operations) >= 100
    assert len(contract.schemas.all) >= 100
    assert len(contract.entities) >= 20

    assert "apps" in {resource.id for resource in contract.resources}
    assert "findApps" in {operation.id for operation in contract.operations}
    assert "AppListQuery" in {schema.id for schema in contract.schemas.dtos}
    assert "AppStatus" in {schema.id for schema in contract.schemas.enums}
    assert "apps.App" in {entity.id for entity in contract.entities}

    assert "App" in normalized_entities.entities.by_id
    assert "admin" in normalized_frontends.by_id
    assert "apps" in normalized_codegen.resources.by_id
    assert "findApps" in normalized_codegen.operations.by_id
    assert contract.meta["loss_count"] == 0


def _contract_signature(contract) -> tuple[object, ...]:
    normalized_entities = contract.meta["normalized_entities"]
    normalized_frontends = contract.meta["normalized_frontends"]
    normalized_codegen = contract.meta["normalized_codegen"]

    return (
        (
            contract.info.title,
            contract.info.openapi_version,
            contract.info.api_version,
            contract.info.description,
        ),
        tuple((server.url, server.description) for server in contract.servers),
        tuple(
            (resource.id, resource.path, resource.operations_count)
            for resource in contract.resources
        ),
        tuple(
            (
                operation.id,
                operation.method.value,
                operation.path,
                operation.resource,
            )
            for operation in contract.operations
        ),
        tuple(
            (schema.id, schema.ref, schema.kind.value, schema.resource)
            for schema in contract.schemas.all
        ),
        tuple(
            (entity.id, entity.resource, entity.schema_ref, entity.store)
            for entity in contract.entities
        ),
        tuple(normalized_entities.by_id),
        tuple(normalized_frontends.by_id),
        tuple(normalized_codegen.resources.by_id),
        tuple(normalized_codegen.operations.by_id),
        contract.meta["loss_count"],
        contract.meta["unresolved_count"],
        contract.meta["cycle_count"],
    )
