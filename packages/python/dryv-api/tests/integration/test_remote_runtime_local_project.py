from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

import pytest

from dryv.features.serialization import contract_to_json
from dryv.ir import Contract, Group, Name, Schema, SchemaField, SchemaKind, SemanticId, TypeExpression
from dryv_cli.api_stdio import StdioApiTransport
from dryv_cli.project_client import (
    ProjectClientError,
    apply_build_events,
    load_managed_outputs,
    project_snapshot,
)


def sid(value: str) -> SemanticId:
    return SemanticId(value)


def precompiled_contract() -> Contract:
    user = Schema(
        sid("remote.schema.user"),
        Name("User"),
        SchemaKind.OBJECT,
        fields=(
            SchemaField(
                sid("remote.schema.user.field.email"),
                Name("email"),
                TypeExpression.primitive("string"),
                required=True,
            ),
        ),
    )
    return Contract(
        sid("remote.application"),
        Name("RemoteApplication"),
        groups=(Group(sid("remote.group"), Name("Remote"), ("remote",), schemas=(user,)),),
    )


def resource(resource_id: str, media_type: str, content: bytes) -> dict[str, object]:
    return {
        "resourceId": resource_id,
        "mediaType": media_type,
        "contentBase64": base64.b64encode(content).decode("ascii"),
    }


def common_pack(template: bytes, *, output_path: str, dependency: str | None) -> dict[str, object]:
    manifest = {
        "apiVersion": "dryv.dev/v1",
        "id": "remote/reference",
        "version": "1.0.0",
        "selections": {"types": {"paths": ["generated"], "select": "groups.schemas.objects.each"}},
    }
    semantic_dependencies = [] if dependency is None else [dependency]
    return {
        "resources": [
            resource(
                "resource://pack/remote/dryv.pack.yaml",
                "application/yaml",
                b"apiVersion: dryv.dev/v1\nid: remote/reference\nversion: 1.0.0\n",
            ),
            resource(
                "resource://pack/remote/templates/type.jinja",
                "text/x-jinja-template",
                template,
            ),
        ],
        "packs": [
            {
                "manifest": manifest,
                "manifestResourceId": "resource://pack/remote/dryv.pack.yaml",
                "templates": [
                    {
                        "resourceId": "resource://pack/remote/templates/type.jinja",
                        "relativePath": "templates/{types}/type.jinja",
                        "mediaType": "text/x-jinja-template",
                        "rendererCapability": "jinja/v1",
                        "selectionKey": "types",
                    }
                ],
            }
        ],
        "planningCandidates": [
            {
                "invocationId": "invocation.remote-user",
                "packId": "remote/reference",
                "selectionKey": "types",
                "templateResourceId": "resource://pack/remote/templates/type.jinja",
                "rendererCapability": "jinja/v1",
                "semanticIds": [] if dependency is None else [dependency],
                "outputId": "artifact.remote-user",
                "outputPath": output_path,
                "context": {"schema": {"name": "User"}},
                "semanticDependencies": semantic_dependencies,
            }
        ],
        "renderSessionIds": ["jinja.remote"],
    }


def precompiled_document(*, previous=None, snapshot=None, template=None) -> dict[str, object]:
    pack = common_pack(
        template or b"export interface {{ schema.name }} {}\n",
        output_path="generated/user.ts",
        dependency="remote.schema.user",
    )
    return {
        "apiVersion": "dryv.api/v1",
        "buildId": "remote-precompiled",
        "resources": [
            resource(
                "resource://project/remote.ir.json",
                "application/vnd.dryv.ir+json",
                contract_to_json(precompiled_contract(), pretty=False).encode(),
            ),
            *pack["resources"],
        ],
        "packs": pack["packs"],
        "planningCandidates": pack["planningCandidates"],
        "precompiledIrResourceId": "resource://project/remote.ir.json",
        "renderSessionIds": pack["renderSessionIds"],
        "previousManagedOutputs": previous or [],
        "projectSnapshot": snapshot
        or [{"path": "generated/user.ts", "exists": False, "contentHash": None}],
    }


def author_document(*, bad_source: bool = False) -> dict[str, object]:
    source = (
        "from dryv_author import Author, field\n"
        "def build_author():\n"
        "    author = Author('remote-authored')\n"
        "    group = author.group('Users')\n"
        "    author.schema('User', {'email': field(str, required=True)}, group=group)\n"
        "    return author\n"
    )
    if bad_source:
        source = "VALUE = 1\n"
    pack = common_pack(
        b"export interface {{ schema.name }}FromAuthor {}\n",
        output_path="generated/authored-user.ts",
        dependency=None,
    )
    return {
        "apiVersion": "dryv.api/v1",
        "buildId": "remote-authored",
        "resources": [
            resource("resource://project/author.py", "text/x-python", source.encode()),
            *pack["resources"],
        ],
        "packs": pack["packs"],
        "planningCandidates": pack["planningCandidates"],
        "author": {
            "connectionId": "python.remote",
            "request": {
                "protocolVersion": 1,
                "jobId": "author.remote",
                "requestedIrVersion": "dryv.ir/2.0.0",
                "sourceKind": "python",
                "sources": [
                    {"resourceId": "resource://project/author.py", "mediaType": "text/x-python"}
                ],
                "options": {},
            },
        },
        "renderSessionIds": pack["renderSessionIds"],
        "previousManagedOutputs": [],
        "projectSnapshot": [
            {"path": "generated/authored-user.ts", "exists": False, "contentHash": None}
        ],
    }


def transport(repo_root: Path) -> StdioApiTransport:
    render_config = [
        {
            "id": "jinja.remote",
            "command": [sys.executable, "-m", "dryv_template_jinja.stdio"],
            "cwd": str(repo_root),
        }
    ]
    author_config = [
        {
            "id": "python.remote",
            "command": [sys.executable, "-m", "dryv_author.stdio"],
            "cwd": str(repo_root),
        }
    ]
    return StdioApiTransport(
        (sys.executable, "-m", "dryv_api.stdio"),
        cwd=repo_root,
        env={
            "DRYV_RENDER_CONNECTIONS_JSON": json.dumps(render_config),
            "DRYV_AUTHOR_CONNECTIONS_JSON": json.dumps(author_config),
        },
    )


def build_result(events) -> dict[str, object]:
    events = tuple(events)
    assert events[0]["type"] == "build-result"
    return events[0]["result"]


def test_remote_precompiled_ir_never_sends_project_root_and_client_applies_locally(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[5]
    document = precompiled_document()
    assert str(tmp_path) not in json.dumps(document)

    with transport(repo_root) as api:
        hello = api.hello()
        assert hello["host"] == "dryv-api"
        events = tuple(api.build_events(document))

    result = events[0]["result"]
    assert result["renderComplete"] is True
    assert result["success"] is True
    assert "applyComplete" not in result

    applied = apply_build_events(tmp_path, events)
    assert applied["renderComplete"] is True
    assert applied["applyComplete"] is True
    assert (tmp_path / "generated/user.ts").read_text() == "export interface User {}\n"


def test_remote_python_author_backend_feeds_same_runtime_without_project_fs(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[5]
    document = author_document()
    assert str(tmp_path) not in json.dumps(document)

    with transport(repo_root) as api:
        events = tuple(api.build_events(document))

    result = events[0]["result"]
    assert result["success"] is True
    assert any(item["stage"] == "authoring" for item in result["trace"])
    applied = apply_build_events(tmp_path, events)
    assert applied["applyComplete"] is True
    assert (tmp_path / "generated/authored-user.ts").read_text() == (
        "export interface UserFromAuthor {}\n"
    )


def test_remote_detects_user_modified_managed_output_before_instruction(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[5]
    with transport(repo_root) as api:
        first_events = tuple(api.build_events(precompiled_document()))
        apply_build_events(tmp_path, first_events)
        previous = load_managed_outputs(tmp_path)
        (tmp_path / "generated/user.ts").write_text("// user edit\n")
        snapshot = project_snapshot(tmp_path, ["generated/user.ts"])
        second = build_result(
            api.build_events(precompiled_document(previous=previous, snapshot=snapshot))
        )
    assert second["success"] is False
    assert any(item["code"] == "ARTIFACT_USER_MODIFIED" for item in second["diagnostics"])


def test_project_client_rechecks_hash_if_file_changes_after_render_complete(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[5]
    with transport(repo_root) as api:
        first_events = tuple(api.build_events(precompiled_document()))
        apply_build_events(tmp_path, first_events)
        previous = load_managed_outputs(tmp_path)
        snapshot = project_snapshot(tmp_path, ["generated/user.ts"])
        second_events = tuple(
            api.build_events(precompiled_document(previous=previous, snapshot=snapshot))
        )

    (tmp_path / "generated/user.ts").write_text("// changed after render_complete\n")
    with pytest.raises(ProjectClientError) as caught:
        apply_build_events(tmp_path, second_events)
    assert caught.value.code == "CLIENT_APPLY_CONFLICT"


def test_renderer_and_author_backend_failures_never_claim_render_complete(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[5]
    with transport(repo_root) as api:
        broken_renderer = build_result(
            api.build_events(
                precompiled_document(template=b"{{ missing.required }}")
            )
        )
        broken_author = build_result(api.build_events(author_document(bad_source=True)))

    assert broken_renderer["success"] is False
    assert broken_renderer["renderComplete"] is False
    assert broken_author["success"] is False
    assert broken_author["renderComplete"] is False
