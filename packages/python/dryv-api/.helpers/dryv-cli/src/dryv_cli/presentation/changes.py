from __future__ import annotations

from dryv_cli.filesystem import ApplyResult, ChangeKind, ChangeSet

from .console import Console

_SYMBOLS = {
    ChangeKind.CREATE: "+",
    ChangeKind.UPDATE: "~",
    ChangeKind.UNCHANGED: "=",
    ChangeKind.CONFLICT: "!",
}


def render_changes(console: Console, changes: ChangeSet) -> None:
    console.write(
        "Changes: "
        + " ".join(
            f"{kind.value}={changes.count(kind)}"
            for kind in (ChangeKind.CREATE, ChangeKind.UPDATE, ChangeKind.UNCHANGED, ChangeKind.CONFLICT)
        )
    )
    for change in changes.changes:
        console.write(f"{_SYMBOLS[change.kind]} {change.artifact.path} · {change.reason}")


def render_apply_result(console: Console, result: ApplyResult) -> None:
    console.write(
        f"Applied: created={len(result.created)} updated={len(result.updated)} unchanged={len(result.unchanged)}"
    )


__all__ = ["render_apply_result", "render_changes"]
