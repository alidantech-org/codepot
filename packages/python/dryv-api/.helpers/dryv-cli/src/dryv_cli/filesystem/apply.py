from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from .diff import ChangeKind, ChangeSet
from .inspect import ManagedOutput, ManagedState, managed_document
from .paths import FilesystemError, MANAGED_STATE_PATH, safe_project_path
from .stage import stage_changes


@dataclass(frozen=True, slots=True)
class ApplyResult:
    created: tuple[str, ...]
    updated: tuple[str, ...]
    unchanged: tuple[str, ...]
    state_path: str = MANAGED_STATE_PATH


class ApplyError(FilesystemError):
    pass


def apply_changes(root: Path, changes: ChangeSet, previous_state: ManagedState) -> ApplyResult:
    root = root.resolve()
    if changes.root != root:
        raise ApplyError("CLI_FS_ROOT", "ChangeSet belongs to a different project root")
    if changes.conflicts:
        paths = ", ".join(item.artifact.path for item in changes.conflicts)
        raise ApplyError("CLI_FS_CONFLICT", f"refusing to apply conflicting generated files: {paths}")

    created: list[str] = []
    updated: list[str] = []
    unchanged = [item.artifact.path for item in changes.changes if item.kind is ChangeKind.UNCHANGED]
    applied: list[tuple[ChangeKind, Path, Path | None]] = []

    with stage_changes(changes) as staged:
        backup_root = staged.root / "backups"
        backup_root.mkdir(parents=True, exist_ok=True)
        state_path = safe_project_path(root, MANAGED_STATE_PATH, internal=True)
        state_backup = backup_root / "managed-state"
        state_existed = state_path.is_file()
        if state_existed:
            shutil.copy2(state_path, state_backup)
        try:
            for index, item in enumerate(staged.files):
                change = item.change
                target = safe_project_path(root, change.artifact.path)
                target.parent.mkdir(parents=True, exist_ok=True)
                backup: Path | None = None
                if change.kind is ChangeKind.UPDATE:
                    backup = backup_root / f"{index:08d}"
                    shutil.copy2(target, backup)
                    try:
                        os.chmod(item.staged_path, target.stat().st_mode)
                    except OSError:
                        pass
                os.replace(item.staged_path, target)
                applied.append((change.kind, target, backup))
                if change.kind is ChangeKind.CREATE:
                    created.append(change.artifact.path)
                else:
                    updated.append(change.artifact.path)

            next_state = _next_state(previous_state, changes)
            _write_state(state_path, next_state)
        except Exception as exc:
            _rollback(applied)
            if state_existed and state_backup.exists():
                state_path.parent.mkdir(parents=True, exist_ok=True)
                os.replace(state_backup, state_path)
            elif not state_existed and state_path.exists():
                state_path.unlink(missing_ok=True)
            raise ApplyError("CLI_FS_APPLY", f"failed applying generated files: {exc}") from exc

    return ApplyResult(tuple(created), tuple(updated), tuple(unchanged))


def _next_state(previous: ManagedState, changes: ChangeSet) -> ManagedState:
    by_path = previous.by_path()
    for change in changes.changes:
        artifact = change.artifact
        by_path[artifact.path] = ManagedOutput(
            artifact.artifact_id,
            artifact.path,
            artifact.content_hash,
            changes.plan_hash,
        )
    return ManagedState(tuple(sorted(by_path.values(), key=lambda item: item.path)))


def _write_state(path: Path, state: ManagedState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    payload = json.dumps(managed_document(state), ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n"
    with temporary.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _rollback(applied: list[tuple[ChangeKind, Path, Path | None]]) -> None:
    for kind, target, backup in reversed(applied):
        try:
            if kind is ChangeKind.CREATE:
                target.unlink(missing_ok=True)
            elif backup is not None and backup.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(backup, target)
        except OSError:
            continue


__all__ = ["ApplyError", "ApplyResult", "apply_changes"]
