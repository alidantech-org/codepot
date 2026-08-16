from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from dryv_api import PackBundleUpload, PackResourceUpload

from dryv_cli.project import LocalProject, PackLocator, ProjectError

from .resources import guess_media_type, upload_bytes

_MANIFEST_NAMES = ("dryv.pack.yaml", "dryv.pack.yml", "dryv.pack.json")


@dataclass(frozen=True, slots=True)
class ResolvedPack:
    upload: PackBundleUpload
    source_root: Path


def resolve_packs(project: LocalProject) -> tuple[ResolvedPack, ...]:
    return tuple(_resolve_pack(project.root, locator) for locator in project.locators.packs)


def _resolve_pack(project_root: Path, locator: PackLocator) -> ResolvedPack:
    if locator.local is None:
        kind = "git" if locator.git is not None else "resource"
        raise ProjectError(
            "CLI_PACK_SOURCE_UNSUPPORTED",
            f"reference CLI currently requires a local pack source; {locator.name!r} uses {kind}",
        )
    root = (project_root / locator.local).resolve(strict=True)
    try:
        root.relative_to(project_root.resolve())
    except ValueError as exc:
        raise ProjectError("CLI_PACK_ESCAPE", f"pack {locator.name!r} escapes project root") from exc
    if not root.is_dir():
        raise ProjectError("CLI_PACK_TYPE", f"pack {locator.name!r} source is not a directory")

    manifests = tuple(root / name for name in _MANIFEST_NAMES if (root / name).is_file())
    if len(manifests) != 1:
        raise ProjectError(
            "CLI_PACK_MANIFEST",
            f"pack {locator.name!r} must contain exactly one of {', '.join(_MANIFEST_NAMES)}",
        )
    manifest_path = manifests[0]
    manifest = upload_bytes(
        f"resource://pack/{locator.name}/manifest",
        "application/dryv-pack+json" if manifest_path.suffix == ".json" else "application/dryv-pack+yaml",
        manifest_path.read_bytes(),
    )
    resources: list[PackResourceUpload] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file() and item != manifest_path):
        relative = path.relative_to(root).as_posix()
        _safe_relative(relative)
        resources.append(
            PackResourceUpload(
                relative,
                upload_bytes(
                    f"resource://pack/{locator.name}/{relative}",
                    guess_media_type(path),
                    path.read_bytes(),
                ),
            )
        )
    return ResolvedPack(PackBundleUpload(locator.name, manifest, tuple(resources)), root)


def _safe_relative(value: str) -> None:
    path = PurePosixPath(value)
    if not value or value.startswith("/") or "\\" in value or any(part in {"", ".", ".."} for part in path.parts):
        raise ProjectError("CLI_PACK_PATH", f"unsafe pack resource path {value!r}")


__all__ = ["ResolvedPack", "resolve_packs"]
