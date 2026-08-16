from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from .diff import ChangeKind, ChangeSet, FileChange
from .inspect import ManagedOutput, ManagedState, inspect_file, load_managed_state, managed_document
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
        raise ApplyError(
            "CLI_FS_CONFLICT",
            f"refusing to apply conflicting generated files: {paths}",
        )

    created: list[str] = []
    updated: list[str] = []
    unchanged = [
        item.artifact.path
        for item in changes.changes
        if item.kind is ChangeKind.UNCHANGED
    ]
    applied: list[tuple[ChangeKind, Path, Path | None]] = []

    with stage_changes(changes) as staged:
        backup_root = staged.root / "backups"
        backup_root.mkdir(parents=True, exist_ok=True)
        state_path = safe_project_path(root, MANAGED_STATE_PATH, internal=True)
        state_backup = backup_root / "managed-state"

        _verify_managed_state(root, previous_state)
        _verify_change_snapshots(root, changes)

        state_existed = state_path.is_file() and not state_path.is_symlink()
        if state_existed:
            shutil.copy2(state_path, state_backup)
        try:
            for index, item in enumerate(staged.files):
                change = item.change
                _verify_change_snapshot(root, change)
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

            _verify_applied_outputs(root, changes)
            _verify_managed_state(root, previous_state)
            next_state = _next_state(previous_state, changes)
            _write_state(state_path, next_state)
        except Exception as exc:
            _rollback(applied)
            if state_existed and state_backup.exists():
                state_path.parent.mkdir(parents=True, exist_ok=True)
                os.replace(state_backup, state_path)
            elif not state_existed and state_path.exists():
                state_path.unlink(missing_ok=True)
            raise ApplyError(
                "CLI_FS_APPLY",
                f"failed applying generated files: {exc}",
            ) from exc

    return ApplyResult(tuple(created), tuple(updated), tuple(unchanged))


def _verify_change_snapshots(root: Path, changes: ChangeSet) -> None:
    for change in changes.changes:
        _verify_change_snapshot(root, change)


def _verify_change_snapshot(root: Path, change: FileChange) -> None:
    current = inspect_file(root, change.artifact.path)
    if current != change.existing:
        raise ApplyError(
            "CLI_FS_CHANGED",
            f"local target changed after diff: {change.artifact.path}",
            path=change.artifact.path,
        )


def _verify_applied_outputs(root: Path, changes: ChangeSet) -> None:
    for change in changes.changes:
        current = inspect_file(root, change.artifact.path)
        if (
            not current.exists
            or not current.regular
            or current.content_hash != change.artifact.content_hash
            or current.size != change.artifact.size
        ):
            raise ApplyError(
                "CLI_FS_APPLY_VERIFY",
                f"generated target does not match verified artifact bytes: {change.artifact.path}",
                path=change.artifact.path,
            )


def _verify_managed_state(root: Path, expected: ManagedState) -> None:
    current = load_managed_state(root)
    if current != expected:
        raise ApplyError(
            "CLI_FS_STATE_CHANGED",
            "managed output state changed after the generation diff was prepared",
            path=MANAGED_STATE_PATH,
        )


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
    payload = (
        json.dumps(
            managed_document(state),
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        ).encode("utf-8")
        + b"\n"
    )
    try:
        with temporary.open("wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


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
