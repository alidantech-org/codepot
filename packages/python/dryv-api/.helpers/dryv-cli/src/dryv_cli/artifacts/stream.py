from __future__ import annotations

import base64
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import BinaryIO

from dryv_cli.connections.api import ApiEvent, DryvApiClient
from dryv_cli.generation import PlannedBuild, ProgressSink, publish_events

from .manifest import planned_artifacts
from .model import ArtifactSet, ReceivedArtifact
from .verify import ArtifactVerificationError, safe_artifact_path


@dataclass(slots=True)
class _OpenArtifact:
    artifact_id: str
    path: str
    content_path: Path
    handle: BinaryIO
    digest: object
    next_offset: int = 0
    declared_size: int | None = None


def receive_stream(
    api: DryvApiClient,
    planned: PlannedBuild,
    *,
    progress: ProgressSink | None = None,
) -> ArtifactSet:
    metadata = planned_artifacts(planned.plan)
    workspace = TemporaryDirectory(prefix="dryv-artifacts-")
    root = Path(workspace.name)
    open_items: dict[str, _OpenArtifact] = {}
    completed: dict[str, ReceivedArtifact] = {}
    stream_complete = False
    try:
        for event in publish_events(api.events(planned.build_id), progress):
            if event.type == "artifact.begin":
                _begin(event, metadata, root, open_items, completed)
            elif event.type == "artifact.chunk":
                _chunk(event, open_items)
            elif event.type == "artifact.end":
                artifact = _end(event, metadata, open_items)
                completed[artifact.artifact_id] = artifact
            elif event.type == "artifact.stream.complete":
                stream_complete = True
            elif event.type in {"build.failed", "build.cancelled"}:
                raise ArtifactVerificationError("CLI_BUILD_TERMINATED", f"build ended with {event.type}")
        if not stream_complete:
            raise ArtifactVerificationError("CLI_ARTIFACT_STREAM_INCOMPLETE", "artifact stream ended without completion marker")
        if open_items:
            raise ArtifactVerificationError("CLI_ARTIFACT_STREAM_INCOMPLETE", "artifact stream ended with unfinished artifacts")
        if set(completed) != set(metadata):
            raise ArtifactVerificationError("CLI_ARTIFACT_STREAM_INCOMPLETE", "artifact stream did not return exactly the planned artifacts")
        artifacts = tuple(sorted(completed.values(), key=lambda item: item.provenance.plan_index))
        return ArtifactSet(planned.build_id, planned.plan_hash, artifacts, workspace)
    except Exception:
        for item in open_items.values():
            item.handle.close()
        workspace.cleanup()
        raise


def _begin(
    event: ApiEvent,
    metadata: dict[str, object],
    root: Path,
    open_items: dict[str, _OpenArtifact],
    completed: dict[str, ReceivedArtifact],
) -> None:
    document = event.document
    artifact_id = _string(document.get("artifactId"), "artifactId")
    path = _string(document.get("path"), "path")
    safe_artifact_path(path)
    expected = metadata.get(artifact_id)
    if expected is None or getattr(expected, "path", None) != path:
        raise ArtifactVerificationError("CLI_ARTIFACT_PLAN", f"artifact {artifact_id!r} does not match GenerationPlan")
    if artifact_id in open_items or artifact_id in completed:
        raise ArtifactVerificationError("CLI_ARTIFACT_DUPLICATE", f"artifact {artifact_id!r} started more than once")
    declared = document.get("size")
    if declared is not None and (not isinstance(declared, int) or isinstance(declared, bool) or declared < 0):
        raise ArtifactVerificationError("CLI_ARTIFACT_SIZE", "artifact begin size must be a non-negative integer")
    content_path = root / sha256(artifact_id.encode("utf-8")).hexdigest()
    handle = content_path.open("wb")
    open_items[artifact_id] = _OpenArtifact(artifact_id, path, content_path, handle, sha256(), 0, declared)


def _chunk(event: ApiEvent, open_items: dict[str, _OpenArtifact]) -> None:
    document = event.document
    artifact_id = _string(document.get("artifactId"), "artifactId")
    item = open_items.get(artifact_id)
    if item is None:
        raise ArtifactVerificationError("CLI_ARTIFACT_ORDER", f"chunk arrived before artifact {artifact_id!r} began")
    offset = document.get("offset")
    if not isinstance(offset, int) or isinstance(offset, bool) or offset != item.next_offset:
        raise ArtifactVerificationError("CLI_ARTIFACT_OFFSET", f"artifact {artifact_id!r} chunk offset is invalid")
    try:
        content = base64.b64decode(_string(document.get("contentBase64"), "contentBase64"), validate=True)
    except Exception as exc:
        raise ArtifactVerificationError("CLI_ARTIFACT_BASE64", f"artifact {artifact_id!r} chunk is invalid base64") from exc
    item.handle.write(content)
    item.digest.update(content)  # type: ignore[attr-defined]
    item.next_offset += len(content)


def _end(
    event: ApiEvent,
    metadata: dict[str, object],
    open_items: dict[str, _OpenArtifact],
) -> ReceivedArtifact:
    document = event.document
    artifact_id = _string(document.get("artifactId"), "artifactId")
    item = open_items.pop(artifact_id, None)
    if item is None:
        raise ArtifactVerificationError("CLI_ARTIFACT_ORDER", f"artifact {artifact_id!r} ended without a begin event")
    item.handle.flush()
    item.handle.close()
    size = document.get("size")
    content_hash = _string(document.get("contentHash"), "contentHash")
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        raise ArtifactVerificationError("CLI_ARTIFACT_SIZE", f"artifact {artifact_id!r} end size is invalid")
    actual_hash = f"sha256:{item.digest.hexdigest()}"  # type: ignore[attr-defined]
    if size != item.next_offset or (item.declared_size is not None and item.declared_size != size):
        raise ArtifactVerificationError("CLI_ARTIFACT_SIZE", f"artifact {artifact_id!r} size does not match streamed bytes")
    if content_hash != actual_hash:
        raise ArtifactVerificationError("CLI_ARTIFACT_HASH", f"artifact {artifact_id!r} hash does not match streamed bytes")
    expected = metadata[artifact_id]
    return ReceivedArtifact(artifact_id, item.path, size, content_hash, item.content_path, getattr(expected, "provenance"))


def _string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ArtifactVerificationError("CLI_ARTIFACT_PROTOCOL", f"artifact event {name} must be a non-empty string")
    return value


__all__ = ["receive_stream"]
