from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
import tempfile
from collections.abc import Iterable, Mapping
from pathlib import Path, PurePosixPath

_API_VERSION = "dryv.api/v1"
_STATE_VERSION = "dryv-managed-outputs/v1"
_STATE_PATH = ".dryv/managed-outputs.json"


class ProjectClientError(ValueError):
    def __init__(self, code: str, message: str, *, path: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.path = path


def resource_payload(
    resource_id: str,
    media_type: str,
    content: bytes,
) -> dict[str, object]:
    if not resource_id.startswith("resource://"):
        raise ProjectClientError("CLIENT_RESOURCE_ID", "resource id must use resource://")
    if not media_type or media_type.strip() != media_type:
        raise ProjectClientError("CLIENT_MEDIA_TYPE", "media type must be non-empty and trimmed")
    return {
        "resourceId": resource_id,
        "mediaType": media_type,
        "contentHash": f"sha256:{hashlib.sha256(content).hexdigest()}",
        "contentBase64": base64.b64encode(content).decode("ascii"),
    }


def resource_from_file(
    root: str | Path,
    relative_path: str,
    *,
    resource_id: str,
    media_type: str,
) -> dict[str, object]:
    project_root = Path(root).resolve()
    relative = _safe_relative(relative_path)
    path = project_root.joinpath(*relative.parts)
    try:
        path.resolve(strict=True).relative_to(project_root)
    except (FileNotFoundError, ValueError) as exc:
        raise ProjectClientError(
            "CLIENT_RESOURCE_PATH",
            f"resource path is missing or escapes project root: {relative_path!r}",
            path=relative_path,
        ) from exc
    if not path.is_file():
        raise ProjectClientError(
            "CLIENT_RESOURCE_PATH",
            f"resource path is not a file: {relative_path!r}",
            path=relative_path,
        )
    return resource_payload(resource_id, media_type, path.read_bytes())


def load_managed_outputs(root: str | Path) -> list[dict[str, str]]:
    project_root = Path(root).resolve()
    path = project_root.joinpath(*PurePosixPath(_STATE_PATH).parts)
    if not path.exists():
        return []
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProjectClientError(
            "CLIENT_STATE_INVALID",
            "managed-output state is not valid UTF-8 JSON",
            path=_STATE_PATH,
        ) from exc
    if not isinstance(document, dict) or document.get("version") != _STATE_VERSION:
        raise ProjectClientError(
            "CLIENT_STATE_VERSION",
            "managed-output state version is unsupported",
            path=_STATE_PATH,
        )
    raw = document.get("outputs")
    if not isinstance(raw, list):
        raise ProjectClientError(
            "CLIENT_STATE_INVALID",
            "managed-output state outputs must be an array",
            path=_STATE_PATH,
        )
    outputs: list[dict[str, str]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ProjectClientError("CLIENT_STATE_INVALID", f"managed output {index} is invalid")
        required = ("path", "contentHash", "ownershipId", "artifactId")
        if set(item) != set(required) or not all(isinstance(item[key], str) for key in required):
            raise ProjectClientError("CLIENT_STATE_INVALID", f"managed output {index} is invalid")
        _safe_relative(item["path"])
        outputs.append({key: item[key] for key in required})
    return sorted(outputs, key=lambda item: item["path"])


def project_snapshot(
    root: str | Path,
    paths: Iterable[str],
) -> list[dict[str, object]]:
    project_root = Path(root).resolve()
    result: list[dict[str, object]] = []
    for path_value in sorted(set(paths)):
        relative = _safe_relative(path_value)
        target = project_root.joinpath(*relative.parts)
        if not target.exists():
            result.append({"path": path_value, "exists": False, "contentHash": None})
            continue
        if not target.is_file():
            raise ProjectClientError(
                "CLIENT_SNAPSHOT_TYPE",
                f"project path is not a regular file: {path_value!r}",
                path=path_value,
            )
        result.append(
            {
                "path": path_value,
                "exists": True,
                "contentHash": artifact_content_hash(target.read_bytes()),
            }
        )
    return result


def artifact_content_hash(content: bytes) -> str:
    return f"sha256:v1:artifact-content:{hashlib.sha256(content).hexdigest()}"


def apply_build_events(
    root: str | Path,
    events: Iterable[Mapping[str, object]],
) -> dict[str, object]:
    """Consume a Dryv API artifact stream and atomically apply managed changes locally."""

    project_root = Path(root).resolve()
    project_root.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".dryv-apply-", dir=project_root.parent))
    streamed = staging / "streamed"
    streamed.mkdir(parents=True, exist_ok=True)
    result_document: dict[str, object] | None = None
    artifact_meta: dict[str, dict[str, object]] = {}
    artifact_files: dict[str, Path] = {}
    next_offsets: dict[str, int] = {}
    stream_complete = False

    try:
        for event in events:
            event_type = event.get("type")
            if event_type == "build-result":
                if result_document is not None:
                    raise ProjectClientError("CLIENT_PROTOCOL", "duplicate build-result event")
                result_document = _object(event.get("result"), "build-result.result")
                if result_document.get("apiVersion") != _API_VERSION:
                    raise ProjectClientError("CLIENT_API_VERSION", "unsupported Dryv API response version")
                raw_artifacts = result_document.get("artifacts", [])
                if not isinstance(raw_artifacts, list):
                    raise ProjectClientError("CLIENT_PROTOCOL", "artifacts must be an array")
                for item in raw_artifacts:
                    meta = _object(item, "build-result.artifacts[]")
                    identity = _required_string(meta.get("artifactId"), "artifactId")
                    if identity in artifact_meta:
                        raise ProjectClientError("CLIENT_PROTOCOL", f"duplicate artifact id {identity!r}")
                    _safe_relative(_required_string(meta.get("path"), "path"))
                    artifact_meta[identity] = meta
                    artifact_files[identity] = streamed / hashlib.sha256(identity.encode()).hexdigest()
                    next_offsets[identity] = 0
                continue

            if event_type == "artifact-content":
                if result_document is None:
                    raise ProjectClientError("CLIENT_PROTOCOL", "artifact content arrived before build result")
                identity = _required_string(event.get("artifactId"), "artifactId")
                if identity not in artifact_meta:
                    raise ProjectClientError("CLIENT_PROTOCOL", f"unknown streamed artifact {identity!r}")
                offset = event.get("offset")
                if not isinstance(offset, int) or isinstance(offset, bool) or offset != next_offsets[identity]:
                    raise ProjectClientError("CLIENT_STREAM_OFFSET", f"invalid stream offset for {identity!r}")
                try:
                    chunk = base64.b64decode(
                        _required_string(event.get("contentBase64"), "contentBase64"),
                        validate=True,
                    )
                except Exception as exc:  # noqa: BLE001 - normalized wire error
                    raise ProjectClientError("CLIENT_STREAM_BASE64", "artifact chunk is invalid base64") from exc
                with artifact_files[identity].open("ab") as handle:
                    handle.write(chunk)
                next_offsets[identity] += len(chunk)
                continue

            if event_type == "stream-complete":
                stream_complete = True
                continue

            raise ProjectClientError("CLIENT_PROTOCOL", f"unknown build event type {event_type!r}")

        if result_document is None or not stream_complete:
            raise ProjectClientError("CLIENT_STREAM_INCOMPLETE", "build artifact stream did not complete")
        if not bool(result_document.get("renderComplete")) or not bool(result_document.get("success")):
            return {
                "buildId": result_document.get("buildId"),
                "renderComplete": bool(result_document.get("renderComplete")),
                "applyComplete": False,
                "applied": [],
            }

        for identity, meta in artifact_meta.items():
            path = artifact_files[identity]
            if not path.exists():
                path.write_bytes(b"")
            content = path.read_bytes()
            expected_size = meta.get("size")
            if not isinstance(expected_size, int) or len(content) != expected_size:
                raise ProjectClientError("CLIENT_ARTIFACT_SIZE", f"artifact {identity!r} size mismatch")
            expected_hash = _required_string(meta.get("contentHash"), "contentHash")
            if artifact_content_hash(content) != expected_hash:
                raise ProjectClientError("CLIENT_ARTIFACT_HASH", f"artifact {identity!r} hash mismatch")

        instructions_raw = result_document.get("writeInstructions", [])
        if not isinstance(instructions_raw, list):
            raise ProjectClientError("CLIENT_PROTOCOL", "writeInstructions must be an array")
        instructions = tuple(_object(item, "writeInstructions[]") for item in instructions_raw)
        _validate_instructions(project_root, instructions, artifact_meta, artifact_files)

        next_outputs = result_document.get("nextManagedOutputs", [])
        if not isinstance(next_outputs, list):
            raise ProjectClientError("CLIENT_PROTOCOL", "nextManagedOutputs must be an array")
        applied = _commit(project_root, staging, instructions, artifact_meta, artifact_files, next_outputs)
        return {
            "buildId": result_document.get("buildId"),
            "renderComplete": True,
            "applyComplete": True,
            "applied": applied,
        }
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def _validate_instructions(
    root: Path,
    instructions: tuple[dict[str, object], ...],
    artifact_meta: Mapping[str, dict[str, object]],
    artifact_files: Mapping[str, Path],
) -> None:
    seen: set[str] = set()
    for item in instructions:
        kind = _required_string(item.get("kind"), "write kind")
        path_value = _required_string(item.get("path"), "write path")
        if path_value in seen:
            raise ProjectClientError("CLIENT_DUPLICATE_WRITE", f"duplicate write instruction {path_value!r}")
        seen.add(path_value)
        relative = _safe_relative(path_value)
        target = root.joinpath(*relative.parts)
        expected = item.get("expectedPreviousHash")
        if expected is not None and not isinstance(expected, str):
            raise ProjectClientError("CLIENT_PROTOCOL", "expectedPreviousHash must be a string or null")
        current_hash = None
        if target.exists():
            if not target.is_file():
                raise ProjectClientError("CLIENT_TARGET_TYPE", f"target is not a file: {path_value!r}", path=path_value)
            current_hash = artifact_content_hash(target.read_bytes())

        if kind == "create":
            if target.exists():
                raise ProjectClientError("CLIENT_CREATE_COLLISION", f"create target already exists: {path_value!r}", path=path_value)
        elif kind in {"update", "unchanged", "delete_managed"}:
            if current_hash != expected:
                raise ProjectClientError("CLIENT_APPLY_CONFLICT", f"project path changed before apply: {path_value!r}", path=path_value)
        else:
            raise ProjectClientError("CLIENT_WRITE_KIND", f"unsupported write kind {kind!r}")

        if kind in {"create", "update", "unchanged"}:
            artifact_id = _required_string(item.get("artifactId"), "artifactId")
            if artifact_id not in artifact_meta or artifact_id not in artifact_files:
                raise ProjectClientError("CLIENT_ARTIFACT_MISSING", f"write references missing artifact {artifact_id!r}")


def _commit(
    root: Path,
    staging: Path,
    instructions: tuple[dict[str, object], ...],
    artifact_meta: Mapping[str, dict[str, object]],
    artifact_files: Mapping[str, Path],
    next_outputs: list[object],
) -> list[dict[str, str]]:
    backups = staging / "backups"
    committed: list[tuple[Path, Path | None]] = []
    applied: list[dict[str, str]] = []
    state_content = json.dumps(
        {"version": _STATE_VERSION, "outputs": next_outputs},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8") + b"\n"

    operations: list[tuple[str, str, Path | None, bytes | None]] = []
    for item in instructions:
        kind = _required_string(item.get("kind"), "kind")
        path_value = _required_string(item.get("path"), "path")
        if kind == "unchanged":
            applied.append({"path": path_value, "kind": kind})
            continue
        if kind == "delete_managed":
            operations.append(("delete", path_value, None, None))
            continue
        artifact_id = _required_string(item.get("artifactId"), "artifactId")
        operations.append(("write", path_value, artifact_files[artifact_id], None))

    operations.append(("write-bytes", _STATE_PATH, None, state_content))
    try:
        for operation, path_value, source, content in operations:
            relative = _safe_relative(path_value)
            target = root.joinpath(*relative.parts)
            backup: Path | None = None
            if target.exists():
                backup = backups.joinpath(*relative.parts)
                backup.parent.mkdir(parents=True, exist_ok=True)
                os.replace(target, backup)
            try:
                if operation == "delete":
                    pass
                elif operation == "write":
                    assert source is not None
                    target.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(source, target)
                elif operation == "write-bytes":
                    assert content is not None
                    pending = staging / "state-pending"
                    pending.write_bytes(content)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(pending, target)
                else:
                    raise ProjectClientError("CLIENT_COMMIT", f"unknown apply operation {operation!r}")
            except Exception:
                if backup is not None and backup.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(backup, target)
                raise
            committed.append((target, backup))
            if path_value != _STATE_PATH:
                applied.append({"path": path_value, "kind": "delete_managed" if operation == "delete" else "write"})
    except Exception:
        for target, backup in reversed(committed):
            try:
                if target.exists():
                    target.unlink()
                if backup is not None and backup.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(backup, target)
            except OSError:
                pass
        raise
    return sorted(applied, key=lambda item: item["path"])


def _safe_relative(path: str) -> PurePosixPath:
    if not isinstance(path, str) or not path or path.startswith("/") or "\\" in path:
        raise ProjectClientError("CLIENT_PATH", "project paths must be POSIX-relative", path=str(path))
    value = PurePosixPath(path)
    if any(part in {"", ".", ".."} for part in value.parts):
        raise ProjectClientError("CLIENT_PATH", "project paths cannot contain traversal segments", path=path)
    if ":" in value.parts[0]:
        raise ProjectClientError("CLIENT_PATH", "project paths cannot be absolute drive paths", path=path)
    return value


def _object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, Mapping) or not all(isinstance(key, str) for key in value):
        raise ProjectClientError("CLIENT_PROTOCOL", f"{label} must be an object")
    return dict(value)


def _required_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ProjectClientError("CLIENT_PROTOCOL", f"{label} must be a non-empty string")
    return value


__all__ = [
    "ProjectClientError",
    "apply_build_events",
    "artifact_content_hash",
    "load_managed_outputs",
    "project_snapshot",
    "resource_from_file",
    "resource_payload",
]
