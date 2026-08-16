from __future__ import annotations

from pathlib import Path

from dryv_cli.project import ProjectError


def resolve_destination(project_root: Path, override: str | None = None) -> Path:
    root = project_root.resolve()
    if override is None:
        return root
    target = (root / override).resolve(strict=False)
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ProjectError("CLI_DESTINATION_ESCAPE", "destination must remain inside the project root") from exc
    return target


__all__ = ["resolve_destination"]
