from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dryv_api import BuildResourceUpload

from dryv_cli.project import LocalProject, ProjectError

from .resources import safe_local_file, upload_bytes


@dataclass(frozen=True, slots=True)
class ResolvedIr:
    upload: BuildResourceUpload
    source: str


def resolve_ir(project: LocalProject, override: str | None = None) -> ResolvedIr | None:
    locator = override or project.locators.source_ir
    if locator is None:
        return None
    path = safe_local_file(project.root, locator)
    media_type = _media_type(path)
    return ResolvedIr(upload_bytes("resource://project/canonical-ir", media_type, path.read_bytes()), locator)


def _media_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return "application/vnd.dryv.ir+json"
    if suffix == ".jsonl":
        return "application/vnd.dryv.ir+jsonl"
    if suffix in {".yaml", ".yml"}:
        return "application/vnd.dryv.ir+yaml"
    raise ProjectError("CLI_IR_MEDIA_TYPE", f"cannot infer Canonical IR representation from {path.name!r}")


__all__ = ["ResolvedIr", "resolve_ir"]
