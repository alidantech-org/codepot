from __future__ import annotations

import base64
from pathlib import Path

from dryv.features.serialization import contract_to_json
from dryv.ir import (
    Contract,
    Group,
    Name,
    Schema,
    SchemaField,
    SchemaKind,
    SemanticId,
    StorageFieldMapping,
    StorageMapping,
    TypeExpression,
)
from dryv_api import DryvApiService, SessionRegistry
from dryv_cli.project_client import apply_build_events, load_managed_outputs, project_snapshot
from dryv_template_jinja import JinjaRenderSession


def sid(value: str) -> SemanticId:
    return SemanticId(value)


def reference_contract() -> Contract:
    base_id = sid("reference.schema.base_record")
    base_field_id = sid("reference.schema.base_record.field.id")
    user_id = sid("reference.schema.user")
    email_id = sid("reference.schema.user.field.email")

    base = Schema(
        id=base_id,
        name=Name("BaseRecord"),
        kind=SchemaKind.OBJECT,
        fields=(
            SchemaField(
                id=base_field_id,
                name=Name("id"),
                type=TypeExpression.primitive("string"),
                required=True,
                readonly=True,
            ),
        ),
    )
    user = Schema(
        id=user_id,
        name=Name("User"),
        kind=SchemaKind.OBJECT,
        extends=base_id,
        fields=(
            SchemaField(
                id=email_id,
                name=Name("email"),
                type=TypeExpression.primitive("string"),
                required=True,
            ),
        ),
    )
    storage = StorageMapping(
        id=sid("reference.storage.user"),
        name=Name("UserStorage"),
        schema=user_id,
        source="users",
        fields=(StorageFieldMapping(email_id, "email", "varchar", unique=True),),
    )
    group = Group(
        id=sid("reference.group.users"),
        name=Name("Users"),
        path=("reference", "users"),
        schemas=(base, user),
        storage_mappings=(storage,),
    )
    return Contract(
        id=sid("reference.application"),
        name=Name("ReferenceApplication"),
        groups=(group,),
    )


def resource(resource_id: str, media_type: str, content: bytes) -> dict[str, object]:
    return {
        "resourceId": resource_id,
        "mediaType": media_type,
        "contentBase64": base64.b64encode(content).decode("ascii"),
    }


def build_document(contract: Contract, *, previous=None, snapshot=None) -> dict[str, object]:
    schema_template = (
        b"export interface {{ schema.name }} extends {{ schema.extends }} {\n"
        b"{% for field in schema.fields %}  {{ field.name }}: {{ field.type }};"
        b"{% if field.inherited %} // inherited{% endif %}\n{% endfor %}}\n"
    )
    storage_template = (
        b"export const {{ mapping.name }} = { table: \"{{ mapping.source }}\", schema: \"{{ mapping.schema }}\" };\n"
    )
    manifest = {
        "apiVersion": "dryv.dev/v1",
        "id": "reference/typescript",
        "version": "1.0.0",
        "selections": {
            "schemaTypes": {"paths": ["src"], "select": "groups.schemas.objects.each"},
            "storageEntities": {"paths": ["src"], "select": "groups.storage.mappings.each"},
        },
    }
    return {
        "apiVersion": "dryv.api/v1",
        "buildId": "reference-build",
        "resources": [
            resource(
                "resource://project/reference.ir.json",
                "application/vnd.dryv.ir+json",
                contract_to_json(contract, pretty=False).encode(),
            ),
            resource(
                "resource://pack/reference/dryv.pack.yaml",
                "application/yaml",
                b"apiVersion: dryv.dev/v1\nid: reference/typescript\nversion: 1.0.0\n",
            ),
            resource(
                "resource://pack/reference/templates/schema.jinja",
                "text/x-jinja-template",
                schema_template,
            ),
            resource(
                "resource://pack/reference/templates/storage.jinja",
                "text/x-jinja-template",
                storage_template,
            ),
        ],
        "packs": [
            {
                "manifest": manifest,
                "manifestResourceId": "resource://pack/reference/dryv.pack.yaml",
                "templates": [
                    {
                        "resourceId": "resource://pack/reference/templates/schema.jinja",
                        "relativePath": "templates/{schemaTypes}/schema.ts.jinja",
                        "mediaType": "text/x-jinja-template",
                        "rendererCapability": "jinja/v1",
                        "selectionKey": "schemaTypes",
                    },
                    {
                        "resourceId": "resource://pack/reference/templates/storage.jinja",
                        "relativePath": "templates/{storageEntities}/storage.ts.jinja",
                        "mediaType": "text/x-jinja-template",
                        "rendererCapability": "jinja/v1",
                        "selectionKey": "storageEntities",
                    },
                ],
            }
        ],
        "planningCandidates": [
            {
                "invocationId": "invocation.user-schema",
                "packId": "reference/typescript",
                "selectionKey": "schemaTypes",
                "templateResourceId": "resource://pack/reference/templates/schema.jinja",
                "rendererCapability": "jinja/v1",
                "semanticIds": ["reference.schema.user"],
                "outputId": "artifact.user-schema",
                "outputPath": "src/user.ts",
                "context": {
                    "schema": {
                        "name": "User",
                        "extends": "BaseRecord",
                        "fields": [
                            {"name": "id", "type": "string", "inherited": True},
                            {"name": "email", "type": "string", "inherited": False},
                        ],
                    }
                },
                "semanticDependencies": [
                    "reference.schema.base_record",
                    "reference.schema.user",
                ],
                "trace": [
                    {
                        "kind": "selection",
                        "subject": "reference.schema.user",
                        "reason": "selected User Schema for schemaTypes",
                    }
                ],
            },
            {
                "invocationId": "invocation.user-storage",
                "packId": "reference/typescript",
                "selectionKey": "storageEntities",
                "templateResourceId": "resource://pack/reference/templates/storage.jinja",
                "rendererCapability": "jinja/v1",
                "semanticIds": ["reference.storage.user"],
                "outputId": "artifact.user-storage",
                "outputPath": "src/user.storage.ts",
                "context": {
                    "mapping": {"name": "UserStorage", "source": "users", "schema": "User"}
                },
                "semanticDependencies": [
                    "reference.schema.user",
                    "reference.storage.user",
                ],
                "trace": [
                    {
                        "kind": "selection",
                        "subject": "reference.storage.user",
                        "reason": "selected UserStorage for storageEntities",
                    }
                ],
            },
        ],
        "precompiledIrResourceId": "resource://project/reference.ir.json",
        "renderSessionIds": ["jinja.local"],
        "previousManagedOutputs": previous or [],
        "projectSnapshot": snapshot
        or [
            {"path": "src/user.ts", "exists": False, "contentHash": None},
            {"path": "src/user.storage.ts", "exists": False, "contentHash": None},
        ],
    }


def service() -> DryvApiService:
    sessions = SessionRegistry()
    sessions.register_renderer("jinja.local", JinjaRenderSession(max_concurrency=2))
    return DryvApiService(sessions=sessions)


def test_reference_pack_reaches_local_project_only_through_api_artifacts(tmp_path: Path) -> None:
    api = service()
    document = build_document(reference_contract())
    events = tuple(api.build_events(document, artifact_chunk_bytes=9))

    result_event = events[0]["result"]
    assert result_event["renderComplete"] is True
    assert result_event["success"] is True
    assert {item["path"] for item in result_event["artifacts"]} == {
        "src/user.ts",
        "src/user.storage.ts",
    }
    assert all("contentBase64" not in item for item in result_event["artifacts"])
    assert sum(1 for item in events if item["type"] == "artifact-content") > 2

    applied = apply_build_events(tmp_path, events)
    assert applied["renderComplete"] is True
    assert applied["applyComplete"] is True
    assert (tmp_path / "src/user.ts").read_text() == (
        "export interface User extends BaseRecord {\n"
        "  id: string; // inherited\n"
        "  email: string;\n"
        "}\n"
    )
    assert (tmp_path / "src/user.storage.ts").read_text() == (
        'export const UserStorage = { table: "users", schema: "User" };\n'
    )


def test_reference_pack_second_build_is_unchanged_and_cacheable(tmp_path: Path) -> None:
    api = service()
    first_events = tuple(api.build_events(build_document(reference_contract())))
    first = apply_build_events(tmp_path, first_events)
    assert first["applyComplete"]

    previous = load_managed_outputs(tmp_path)
    snapshot = project_snapshot(tmp_path, [item["path"] for item in previous])
    second_events = tuple(
        api.build_events(build_document(reference_contract(), previous=previous, snapshot=snapshot))
    )
    result = second_events[0]["result"]
    assert result["cache"]["contextHits"] == 2
    assert result["cache"]["renderHits"] == 2
    assert {item["kind"] for item in result["writeInstructions"]} == {"unchanged"}
