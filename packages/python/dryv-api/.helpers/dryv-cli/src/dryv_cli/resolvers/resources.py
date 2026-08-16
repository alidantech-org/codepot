from __future__ import annotations

import mimetypes
from hashlib import sha256
from pathlib import Path

from dryv_api import BuildResourceUpload

from dryv_cli.project import LocalProject, ProjectError


def resolve_project_resources(project: LocalProject) -> tuple[BuildResourceUpload, ...]:
    result: list[BuildResourceUpload] = []
    for resource_id in project.locators.resources:
        prefix = "resource://project/"
        if not resource_id.startswith(prefix):
            raise ProjectError(
                "CLI_RESOURCE_LOCATOR",
                f"local project resource {resource_id!r} must use resource://project/<relative-path>",
            )
        relative = resource_id.removeprefix(prefix)
        result.append(upload_file(project.root, relative, resource_id=resource_id))
    return tuple(result)


def upload_bytes(resource_id: str, media_type: str, content: bytes) -> BuildResourceUpload:
    return BuildResourceUpload(
        resource_id=resource_id,
        media_type=media_type,
        content=content,
        content_hash=f"sha256:{sha256(content).hexdigest()}",
    )


def upload_file(root: Path, relative_path: str, *, resource_id: str, media_type: str | None = None) -> BuildResourceUpload:
    target = safe_local_file(root, relative_path)
    return upload_bytes(resource_id, media_type or guess_media_type(target), target.read_bytes())


def safe_local_file(root: Path, relative_path: str) -> Path:
    root = root.resolve()
    target = (root / relative_path).resolve(strict=True)
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ProjectError("CLI_RESOURCE_ESCAPE", f"resource escapes project root: {relative_path!r}") from exc
    if not target.is_file():
        raise ProjectError("CLI_RESOURCE_TYPE", f"resource is not a regular file: {relative_path!r}")
    return target


def guess_media_type(path: Path) -> str:
    suffixes = "".join(path.suffixes[-2:]).lower()
    if suffixes in {".pack.yaml", ".pack.yml"}:
        return "application/dryv-pack+yaml"
    if suffixes == ".pack.json":
        return "application/dryv-pack+json"
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed or "application/octet-stream"


__all__ = ["guess_media_type", "resolve_project_resources", "safe_local_file", "upload_bytes", "upload_file"]
