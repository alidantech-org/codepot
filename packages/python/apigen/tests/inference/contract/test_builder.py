"""Tests for building API contracts from inference graphs."""

from __future__ import annotations

from src.inference.contract import build_api_contract
from src.inference.models import (
    InferenceGraph,
    InferredResource,
    InferredSchema,
    InferredSchemaKind,
)
from src.inference.models.schemas import InferredSchemaField
from tests.fixtures.openapi import load_sample_graph


def test_build_api_contract_from_sample_openapi(sample_openapi_path) -> None:
    graph = load_sample_graph(sample_openapi_path)
    api = build_api_contract(graph)

    assert api.info.title
    assert api.info.openapi_version.startswith("3.")
    assert len(api.schemas.all) > 0
    assert len(api.operations) > 0


def test_api_contract_preserves_openapi_servers(sample_openapi_path) -> None:
    graph = load_sample_graph(sample_openapi_path)
    api = build_api_contract(graph)

    assert api.servers
    assert api.servers[0].url == "https://api.riderescueautolink.com"
    assert api.servers[0].description == "Riderescue API"


def test_api_contract_preserves_operation_facts(sample_openapi_path) -> None:
    graph = load_sample_graph(sample_openapi_path)
    api = build_api_contract(graph)

    operation = api.operations[0]

    assert operation.id
    assert operation.method
    assert operation.path


def test_api_contract_preserves_resource_path(sample_openapi_path) -> None:
    graph = load_sample_graph(sample_openapi_path)
    api = build_api_contract(graph)

    resource = next(resource for resource in api.resources if resource.id == "users")

    assert resource.path == ("platform", "auth")
    assert resource.path_name is not None
    assert resource.path_name.path.original == "platform_auth"


def test_api_contract_parses_root_codegen_entities() -> None:
    resource = InferredResource(name="apps", path=("platform",))
    graph = InferenceGraph(
        title="Entity API",
        openapi_version="3.1.0",
        api_version="v1",
        description="-",
        servers=(),
        resources=(resource,),
        schemas=(
            InferredSchema(
                name="App",
                ref="#/components/schemas/App",
                kind=InferredSchemaKind.MODEL,
                resource=resource,
                fields=(
                    InferredSchemaField(
                        name="id",
                        required=True,
                        nullable=False,
                        raw_type="string",
                        format="uuid",
                        resolved_kind="primitive",
                        resolved_type="string",
                        resolved_format="uuid",
                    ),
                    InferredSchemaField(
                        name="slug",
                        required=True,
                        nullable=False,
                        raw_type="string",
                        resolved_kind="primitive",
                        resolved_type="string",
                    ),
                ),
            ),
        ),
        operations=(),
        dependencies=(),
        x_codegen={
            "entities": {
                "apps": {
                    "App": {
                        "resource": {"$ref": "#/x-codegen/resources/apps"},
                        "schema": {"$ref": "#/components/schemas/App"},
                        "store": "apps",
                        "fields": {
                            "id": {"role": "primaryKey", "generated": "uuid"},
                        },
                        "backend": {
                            "keyHash": {"type": "string"},
                        },
                        "constraints": {
                            "app_slug_unique": {"kind": "unique", "fields": ["slug"]},
                        },
                        "relations": {
                            "apiKeys": {
                                "cardinality": "hasMany",
                                "target": {"$ref": "#/x-codegen/entities/apps/AppApiKey"},
                                "local": "id",
                                "foreign": "appId",
                            },
                        },
                    },
                },
            },
        },
    )

    api = build_api_contract(graph)

    assert len(api.entities) == 1
    entity = api.entities[0]
    assert entity.id == "apps.App"
    assert entity.resource == "apps"
    assert entity.schema_ref == "#/components/schemas/App"
    assert entity.store == "apps"
    assert tuple(field.id for field in entity.fields) == ("id", "slug")
    assert entity.fields[0].meta["x-codegen"]["role"] == "primaryKey"
    assert entity.backend_fields[0].id == "keyHash"
    assert entity.backend_fields[0].meta["backend_only"] is True
    assert entity.constraints[0].kind == "unique"
    assert entity.constraints[0].fields == ("slug",)
    assert entity.relations[0].cardinality == "hasMany"
    assert entity.relations[0].target_ref == "#/x-codegen/entities/apps/AppApiKey"
