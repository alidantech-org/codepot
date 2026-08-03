"""Tests for building API contracts from inference graphs."""

from __future__ import annotations

from archives.codepotg.src.inference.contract import build_api_contract
from archives.codepotg.src.inference.models import (
    InferenceGraph,
    InferredResource,
    InferredSchema,
    InferredSchemaKind,
)
from archives.codepotg.src.inference.models.schemas import InferredSchemaField
from archives.codepotg.tests.fixtures.openapi import load_real_graph

from contracts.api import ApiHttpMethod


def test_api_contract_preserves_real_openapi(real_openapi_path) -> None:
    graph = load_real_graph(real_openapi_path)
    api = build_api_contract(graph)

    assert api.info.title == "Alidantech API"
    assert api.info.openapi_version == "3.1.0"
    assert api.servers
    assert api.servers[0].url == "http://localhost:5000"
    assert api.servers[0].description == "Alidantech API (Local)"

    assert {resource.id for resource in api.resources} >= {
        "apps",
        "users",
        "analytics",
    }
    assert {operation.id for operation in api.operations} >= {
        "findApps",
        "getAppById",
        "findUsers",
    }
    assert {schema.id for schema in api.schemas.all} >= {
        "App",
        "AppListQuery",
        "AppStatus",
    }

    operation = next(item for item in api.operations if item.id == "findApps")
    assert operation.method == ApiHttpMethod.GET
    assert operation.path == "/platform/apps"
    assert operation.resource == "apps"
    assert operation.description == "List apps"

    resource = next(item for item in api.resources if item.id == "apps")
    assert resource.path == ("platform",)
    assert resource.path_name is not None
    assert resource.path_name.path.original == "platform"

    entity = next(item for item in api.entities if item.id == "apps.App")
    assert entity.name.raw.original == "App"
    assert entity.resource == "apps"
    assert entity.schema_ref == "#/components/schemas/App"
    assert entity.store == "apps"
    assert {field.id for field in entity.fields} >= {
        "name",
        "slug",
        "status",
    }
    assert any(constraint.kind == "unique" for constraint in entity.constraints)


def test_api_contract_parses_legacy_nested_codegen_entities() -> None:
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
                            "app_slug_unique": {
                                "kind": "unique",
                                "fields": ["slug"],
                            },
                        },
                        "relations": {
                            "apiKeys": {
                                "cardinality": "hasMany",
                                "target": {
                                    "$ref": "#/x-codegen/entities/apps/AppApiKey"
                                },
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
    assert entity.relations[0].target_ref == (
        "#/x-codegen/entities/apps/AppApiKey"
    )
