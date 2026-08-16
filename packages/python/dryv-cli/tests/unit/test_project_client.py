from __future__ import annotations

import base64
from pathlib import Path

import pytest

from dryv_cli.project_client import (
    ProjectClientError,
    apply_build_events,
    artifact_content_hash,
    load_managed_outputs,
    project_snapshot,
)


def events(content: bytes, *, expected: str | None = None, kind: str = "create"):
    content_hash = artifact_content_hash(content)
    result = {
        "apiVersion": "dryv.api/v1",
        "buildId": "build.test",
        "status": "render_complete",
        "success": True,
        "renderComplete": True,
        "artifacts": [
            {
                "artifactId": "artifact.test",
                "path": "generated/test.txt",
                "logicalOutputId": "artifact.test",
                "contentHash": content_hash,
                "ownershipId": "pack:test",
                "size": len(content),
                "status": "render_complete",
                "dependencies": [],
                "provenance": {},
            }
        ],
        "writeInstructions": [
            {
                "kind": kind,
                "path": "generated/test.txt",
                "ownershipId": "pack:test",
                "artifactId": "artifact.test",
                "expectedPreviousHash": expected,
                "newContentHash": content_hash,
                "reason": "test",
            }
        ],
        "nextManagedOutputs": [
            {
                "path": "generated/test.txt",
                "contentHash": content_hash,
                "ownershipId": "pack:test",
                "artifactId": "artifact.test",
            }
        ],
    }
    return (
        {"type": "build-result", "result": result},
        {
            "type": "artifact-content",
            "artifactId": "artifact.test",
            "offset": 0,
            "contentBase64": base64.b64encode(content).decode("ascii"),
            "final": True,
        },
        {"type": "stream-complete", "buildId": "build.test", "renderComplete": True},
    )


def test_create_apply_is_local_atomic_and_persists_managed_state(tmp_path: Path) -> None:
    acknowledgement = apply_build_events(tmp_path, events(b"hello\n"))
    assert acknowledgement["renderComplete"] is True
    assert acknowledgement["applyComplete"] is True
    assert (tmp_path / "generated/test.txt").read_bytes() == b"hello\n"
    managed = load_managed_outputs(tmp_path)
    assert managed[0]["path"] == "generated/test.txt"
    assert managed[0]["contentHash"] == artifact_content_hash(b"hello\n")


def test_project_snapshot_hashes_actual_local_file(tmp_path: Path) -> None:
    path = tmp_path / "generated/test.txt"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"current\n")
    snapshot = project_snapshot(tmp_path, ["generated/test.txt", "generated/missing.txt"])
    assert snapshot == [
        {
            "path": "generated/missing.txt",
            "exists": False,
            "contentHash": None,
        },
        {
            "path": "generated/test.txt",
            "exists": True,
            "contentHash": artifact_content_hash(b"current\n"),
        },
    ]


def test_apply_rechecks_expected_hash_immediately_before_mutation(tmp_path: Path) -> None:
    path = tmp_path / "generated/test.txt"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"old\n")
    expected = artifact_content_hash(b"old\n")
    streamed = events(b"new\n", expected=expected, kind="update")
    path.write_bytes(b"user edit\n")

    with pytest.raises(ProjectClientError) as caught:
        apply_build_events(tmp_path, streamed)
    assert caught.value.code == "CLIENT_APPLY_CONFLICT"
    assert path.read_bytes() == b"user edit\n"


def test_failed_render_is_never_applied(tmp_path: Path) -> None:
    failed = (
        {
            "type": "build-result",
            "result": {
                "apiVersion": "dryv.api/v1",
                "buildId": "build.failed",
                "status": "failed",
                "success": False,
                "renderComplete": False,
                "artifacts": [],
                "writeInstructions": [],
                "nextManagedOutputs": [],
            },
        },
        {"type": "stream-complete", "buildId": "build.failed", "renderComplete": False},
    )
    acknowledgement = apply_build_events(tmp_path, failed)
    assert acknowledgement == {
        "buildId": "build.failed",
        "renderComplete": False,
        "applyComplete": False,
        "applied": [],
    }
