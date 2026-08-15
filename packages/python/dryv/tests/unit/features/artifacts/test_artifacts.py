from __future__ import annotations

import pytest

from dryv.features.artifacts import (
    ArtifactError,
    ArtifactFeature,
    GeneratedArtifact,
    ManagedOutput,
    ManagedOutputManifest,
    ProjectPathState,
    ProjectSnapshot,
    WriteKind,
)


def _artifact(content_hash: str = "hash:new", *, path: str = "src/user.ts") -> GeneratedArtifact:
    return GeneratedArtifact(
        artifact_id="artifact.user",
        path=path,
        logical_output_id="output.user",
        content=b"export interface User {}\n",
        content_hash=content_hash,
        ownership_id="pack.example:user",
    )


def test_first_build_classifies_create_without_writing_files() -> None:
    result = ArtifactFeature().classify(
        (_artifact(),),
        snapshot=ProjectSnapshot((ProjectPathState("src/user.ts", False),)),
    )
    instruction = result.instructions[0]
    assert instruction.kind is WriteKind.CREATE
    assert instruction.expected_previous_hash is None
    assert result.next_manifest.outputs[0].content_hash == "hash:new"
    assert result.render_complete


def test_unchanged_and_update_require_matching_previous_managed_hash() -> None:
    previous = ManagedOutputManifest(
        (ManagedOutput("src/user.ts", "hash:old", "pack.example:user", "artifact.user"),)
    )
    snapshot = ProjectSnapshot((ProjectPathState("src/user.ts", True, "hash:old"),))

    unchanged = ArtifactFeature().classify(
        (_artifact("hash:old"),), previous=previous, snapshot=snapshot
    )
    assert unchanged.instructions[0].kind is WriteKind.UNCHANGED

    changed = ArtifactFeature().classify(
        (_artifact("hash:new"),), previous=previous, snapshot=snapshot
    )
    assert changed.instructions[0].kind is WriteKind.UPDATE
    assert changed.instructions[0].expected_previous_hash == "hash:old"


def test_stale_output_can_only_delete_previous_managed_content() -> None:
    previous = ManagedOutputManifest(
        (ManagedOutput("src/old.ts", "hash:old", "pack.example:old", "artifact.old"),)
    )
    result = ArtifactFeature().classify(
        (),
        previous=previous,
        snapshot=ProjectSnapshot((ProjectPathState("src/old.ts", True, "hash:old"),)),
    )
    assert result.instructions[0].kind is WriteKind.DELETE_MANAGED
    assert result.instructions[0].expected_previous_hash == "hash:old"
    assert result.next_manifest.outputs == ()


def test_user_modified_managed_output_is_refused() -> None:
    previous = ManagedOutputManifest(
        (ManagedOutput("src/user.ts", "hash:old", "pack.example:user", "artifact.user"),)
    )
    with pytest.raises(ArtifactError) as caught:
        ArtifactFeature().classify(
            (_artifact("hash:new"),),
            previous=previous,
            snapshot=ProjectSnapshot((ProjectPathState("src/user.ts", True, "hash:user-edit"),)),
        )
    assert caught.value.code == "ARTIFACT_USER_MODIFIED"


def test_unmanaged_collision_and_path_traversal_are_refused() -> None:
    with pytest.raises(ArtifactError) as collision:
        ArtifactFeature().classify(
            (_artifact(),),
            snapshot=ProjectSnapshot((ProjectPathState("src/user.ts", True, "hash:someone"),)),
        )
    assert collision.value.code == "ARTIFACT_UNMANAGED_COLLISION"

    with pytest.raises(ArtifactError) as traversal:
        _artifact(path="../outside.ts")
    assert traversal.value.code == "ARTIFACT_PATH"


def test_artifact_content_stream_is_bounded_into_chunks() -> None:
    artifact = GeneratedArtifact(
        artifact_id="artifact.large",
        path="assets/large.bin",
        logical_output_id="output.large",
        content=b"abcdefghij",
        content_hash="hash:large",
        ownership_id="pack.example:large",
    )
    chunks = tuple(ArtifactFeature().stream_artifact(artifact, chunk_size=4))
    assert [item.content for item in chunks] == [b"abcd", b"efgh", b"ij"]
    assert [item.offset for item in chunks] == [0, 4, 8]
    assert chunks[-1].final
