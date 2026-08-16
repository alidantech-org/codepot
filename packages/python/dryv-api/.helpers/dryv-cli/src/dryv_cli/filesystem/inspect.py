from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from .paths import FilesystemError, MANAGED_STATE_PATH, safe_project_path

MANAGED_STATE_VERSION = "dryv.managed/v1"


@dataclass(frozen=True, slots=True)
class ManagedOutput:
    artifact_id: str
    path: str
    content_hash: str
    plan_hash: str


@dataclass(frozen=True, slots=True)
class ManagedState:
    outputs: tuple[ManagedOutput, ...] = ()

    def by_path(self) -> dict[str, ManagedOutput]:
        return {item.path: item for item in self.outputs}


@dataclass(frozen=True, slots=True)
class ExistingFile:
    path: str
    exists: bool
    regular: bool
    content_hash: str | None
    size: int | None


def load_managed_state(root: Path) -> ManagedState:
    path = safe_project_path(root, MANAGED_STATE_PATH, internal=True)
    if not path.exists():
        return ManagedState()
    if not path.is_file():
        raise FilesystemError("CLI_FS_STATE_TYPE", "managed output state is not a regular file", path=MANAGED_STATE_PATH)
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FilesystemError("CLI_FS_STATE_INVALID", "managed output state is not valid UTF-8 JSON", path=MANAGED_STATE_PATH) from exc
    if not isinstance(document, dict) or document.get("version") != MANAGED_STATE_VERSION:
        raise FilesystemError("CLI_FS_STATE_VERSION", "managed output state version is unsupported", path=MANAGED_STATE_PATH)
    raw = document.get("outputs")
    if not isinstance(raw, list):
        raise FilesystemError("CLI_FS_STATE_INVALID", "managed output state outputs must be an array", path=MANAGED_STATE_PATH)
    outputs: list[ManagedOutput] = []
    for index, value in enumerate(raw):
        if not isinstance(value, dict):
            raise FilesystemError("CLI_FS_STATE_INVALID", f"managed output {index} must be an object")
        artifact_id = _string(value.get("artifactId"), "artifactId")
        relative = _string(value.get("path"), "path")
        safe_project_path(root, relative)
        outputs.append(
            ManagedOutput(
                artifact_id,
                relative,
                _string(value.get("contentHash"), "contentHash"),
                _string(value.get("planHash"), "planHash"),
            )
        )
    paths = tuple(item.path for item in outputs)
    if len(paths) != len(set(paths)):
        raise FilesystemError("CLI_FS_STATE_DUPLICATE", "managed output state paths must be unique")
    return ManagedState(tuple(sorted(outputs, key=lambda item: item.path)))


def inspect_file(root: Path, relative_path: str) -> ExistingFile:
    target = safe_project_path(root, relative_path)
    if not target.exists():
        return ExistingFile(relative_path, False, False, None, None)
    if not target.is_file():
        return ExistingFile(relative_path, True, False, None, None)
    digest = sha256()
    size = 0
    with target.open("rb") as handle:
        while True:
            chunk = handle.read(64 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            size += len(chunk)
    return ExistingFile(relative_path, True, True, f"sha256:{digest.hexdigest()}", size)


def managed_document(state: ManagedState) -> dict[str, object]:
    return {
        "version": MANAGED_STATE_VERSION,
        "outputs": [
            {
                "artifactId": item.artifact_id,
                "path": item.path,
                "contentHash": item.content_hash,
                "planHash": item.plan_hash,
            }
            for item in sorted(state.outputs, key=lambda output: output.path)
        ],
    }


def _string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise FilesystemError("CLI_FS_STATE_INVALID", f"managed output {name} must be a non-empty string")
    return value


__all__ = [
    "ExistingFile",
    "MANAGED_STATE_VERSION",
    "ManagedOutput",
    "ManagedState",
    "inspect_file",
    "load_managed_state",
    "managed_document",
]
