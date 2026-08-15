from __future__ import annotations

import base64
import copy
import sys
from pathlib import Path

from dryv.features.serialization import contract_to_json
from dryv.ir import Contract, Group, Name, Schema, SchemaField, SchemaKind, SemanticId, TypeExpression
from dryv.runtime import DryvRuntime
from dryv_api import DryvApiService, SessionRegistry, SubprocessRenderSession


def sid(value: str) -> SemanticId:
    return SemanticId(value)


def contract(*, user_label: str = "email", include_unrelated: bool = False) -> Contract:
    user = Schema(
        sid("matrix.schema.user"),
        Name("User"),
        SchemaKind.OBJECT,
        fields=(
            SchemaField(
                sid("matrix.schema.user.field.value"),
                Name(user_label),
                TypeExpression.primitive("string"),
                required=True,
            ),
        ),
    )
    audit = Schema(
        sid("matrix.schema.audit"),
        Name("Audit"),
        SchemaKind.OBJECT,
        fields=(
            SchemaField(
                sid("matrix.schema.audit.field.message"),
                Name("message"),
                TypeExpression.primitive("string"),
            ),
        ),
    )
    schemas = [user, audit]
    if include_unrelated:
        schemas.append(
            Schema(
                sid("matrix.schema.unrelated"),
                Name("Unrelated"),
                SchemaKind.OBJECT,
            )
        )
    return Contract(
        sid("matrix.application"),
        Name("MatrixApplication"),
        groups=(
            Group(
                sid("matrix.group"),
                Name("Matrix"),
                ("matrix",),
                schemas=tuple(schemas),
            ),
        ),
    )


def resource(resource_id: str, media_type: str, content: bytes) -> dict[str, object]:
    return {
        "resourceId": resource_id,
        "mediaType": media_type,
        "contentBase64": base64.b64encode(content).decode("ascii"),
    }


def document(
    value: Contract,
    *,
    user_label: str = "email",
    handlebars_template: bytes = b"export type {{schema.name}}Handlebars = string;\n",
    cache_mode: str = "use",
    previous=None,
) -> dict[str, object]:
    manifest = {
        "apiVersion": "dryv.dev/v1",
        "id": "matrix/mixed",
        "version": "1.0.0",
        "selections": {
            "jinjaTypes": {"paths": ["generated"], "select": "groups.schemas.objects.each"},
            "handlebarsTypes": {"paths": ["generated"], "select": "groups.schemas.objects.each"},
        },
    }
    return {
        "apiVersion": "dryv.api/v1",
        "buildId": f"matrix-{user_label}-{cache_mode}",
        "resources": [
            resource(
                "resource://project/matrix.ir.json",
                "application/vnd.dryv.ir+json",
                contract_to_json(value, pretty=False).encode(),
            ),
            resource(
                "resource://pack/mixed/dryv.pack.yaml",
                "application/yaml",
                b"apiVersion: dryv.dev/v1\nid: matrix/mixed\nversion: 1.0.0\n",
            ),
            resource(
                "resource://pack/mixed/templates/user.jinja",
                "text/x-jinja-template",
                b"export type {{ schema.name }}Jinja = {{ schema.field }};\n",
            ),
            resource(
                "resource://pack/mixed/templates/audit.hbs",
                "text/x-handlebars-template",
                handlebars_template,
            ),
        ],
        "packs": [
            {
                "manifest": manifest,
                "manifestResourceId": "resource://pack/mixed/dryv.pack.yaml",
                "templates": [
                    {
                        "resourceId": "resource://pack/mixed/templates/user.jinja",
                        "relativePath": "templates/{jinjaTypes}/user.jinja",
                        "mediaType": "text/x-jinja-template",
                        "rendererCapability": "jinja/v1",
                        "selectionKey": "jinjaTypes",
                    },
                    {
                        "resourceId": "resource://pack/mixed/templates/audit.hbs",
                        "relativePath": "templates/{handlebarsTypes}/audit.hbs",
                        "mediaType": "text/x-handlebars-template",
                        "rendererCapability": "handlebars/v1",
                        "selectionKey": "handlebarsTypes",
                    },
                ],
            }
        ],
        "planningCandidates": [
            {
                "invocationId": "invocation.user",
                "packId": "matrix/mixed",
                "selectionKey": "jinjaTypes",
                "templateResourceId": "resource://pack/mixed/templates/user.jinja",
                "rendererCapability": "jinja/v1",
                "semanticIds": ["matrix.schema.user"],
                "outputId": "artifact.user",
                "outputPath": "generated/user.ts",
                "context": {"schema": {"name": "User", "field": user_label}},
                "semanticDependencies": ["matrix.schema.user"],
            },
            {
                "invocationId": "invocation.audit",
                "packId": "matrix/mixed",
                "selectionKey": "handlebarsTypes",
                "templateResourceId": "resource://pack/mixed/templates/audit.hbs",
                "rendererCapability": "handlebars/v1",
                "semanticIds": ["matrix.schema.audit"],
                "outputId": "artifact.audit",
                "outputPath": "generated/audit.ts",
                "context": {"schema": {"name": "Audit"}},
                "semanticDependencies": ["matrix.schema.audit"],
            },
        ],
        "precompiledIrResourceId": "resource://project/matrix.ir.json",
        "renderSessionIds": ["handlebars.process", "jinja.process"],
        "previousManagedOutputs": previous or [],
        "projectSnapshot": [
            {"path": "generated/audit.ts", "exists": False, "contentHash": None},
            {"path": "generated/user.ts", "exists": False, "contentHash": None},
        ],
        "cacheMode": cache_mode,
    }


def result(service: DryvApiService, payload: dict[str, object]) -> dict[str, object]:
    events = tuple(service.build_events(payload))
    return events[0]["result"]


def sessions(repo_root: Path, *, revision: str = "v1"):
    jinja = SubprocessRenderSession((sys.executable, "-m", "dryv_template_jinja.stdio"))
    handlebars = SubprocessRenderSession(
        (
            "node",
            str(repo_root / "packages/nodejs/codepotx/render-clients/handlebars/stdio.mjs"),
        ),
        cwd=repo_root,
        env={"DRYV_RENDERER_REVISION": revision},
    )
    registry = SessionRegistry()
    registry.register_renderer("jinja.process", jinja)
    registry.register_renderer("handlebars.process", handlebars)
    return registry, jinja, handlebars


def test_two_real_renderer_processes_share_one_runtime_and_cache_matrix() -> None:
    repo_root = Path(__file__).resolve().parents[5]
    runtime = DryvRuntime()
    registry, jinja, handlebars = sessions(repo_root, revision="v1")
    try:
        api = DryvApiService(runtime=runtime, sessions=registry)
        first = result(api, document(contract()))
        assert first["success"] is True
        dispatch = {
            item["details"]["session"]
            for item in first["trace"]
            if item["stage"] == "render-dispatch"
        }
        assert dispatch == {"jinja.process", "handlebars.process"}
        previous = first["nextManagedOutputs"]

        unchanged = result(api, document(contract(), previous=previous))
        assert unchanged["cache"] == {
            "contextHits": 2,
            "contextMisses": 0,
            "renderHits": 2,
            "renderMisses": 0,
        }

        unrelated = result(
            api,
            document(contract(include_unrelated=True), previous=previous),
        )
        assert unrelated["cache"]["contextHits"] == 2
        assert unrelated["cache"]["renderHits"] == 2

        relevant = result(
            api,
            document(contract(user_label="username"), user_label="username", previous=previous),
        )
        assert relevant["cache"]["contextHits"] == 1
        assert relevant["cache"]["contextMisses"] == 1
        assert relevant["cache"]["renderHits"] == 1
        assert relevant["cache"]["renderMisses"] == 1

        changed_template = result(
            api,
            document(
                contract(),
                handlebars_template=b"export interface {{schema.name}}Handlebars {}\n",
                previous=previous,
            ),
        )
        assert changed_template["cache"]["renderHits"] == 1
        assert changed_template["cache"]["renderMisses"] == 1

        refreshed = result(api, document(contract(), cache_mode="refresh", previous=previous))
        assert refreshed["cache"]["contextMisses"] == 2
        assert refreshed["cache"]["renderMisses"] == 2

        off = result(api, document(contract(), cache_mode="off", previous=previous))
        assert off["cache"]["contextMisses"] == 2
        assert off["cache"]["renderMisses"] == 2
    finally:
        handlebars.close()
        jinja.close()

    registry_v2, jinja_v2, handlebars_v2 = sessions(repo_root, revision="v2")
    try:
        api_v2 = DryvApiService(runtime=runtime, sessions=registry_v2)
        fingerprint_changed = result(api_v2, document(contract(), previous=previous))
        assert fingerprint_changed["cache"]["contextHits"] == 2
        assert fingerprint_changed["cache"]["renderHits"] == 1
        assert fingerprint_changed["cache"]["renderMisses"] == 1
    finally:
        handlebars_v2.close()
        jinja_v2.close()
