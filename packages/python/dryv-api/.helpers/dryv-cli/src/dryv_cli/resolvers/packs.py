from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory

from dryv_api import PackBundleUpload, PackResourceUpload

from dryv_cli.project import LocalProject, PackLocator, ProjectError

from .resources import guess_media_type, upload_bytes

_MANIFEST_NAMES = ("dryv.pack.yaml", "dryv.pack.yml", "dryv.pack.json")
_GIT_TIMEOUT_SECONDS = 120


@dataclass(frozen=True, slots=True)
class ResolvedPack:
    upload: PackBundleUpload


def resolve_packs(project: LocalProject) -> tuple[ResolvedPack, ...]:
    return tuple(_resolve_pack(project.root, locator) for locator in project.locators.packs)


def _resolve_pack(project_root: Path, locator: PackLocator) -> ResolvedPack:
    if locator.local is not None:
        root = _local_pack_root(project_root, locator)
        return ResolvedPack(_bundle_pack(root, locator.name))
    if locator.git is not None:
        return ResolvedPack(_bundle_git_pack(locator))
    raise ProjectError(
        "CLI_PACK_RESOURCE_UNSUPPORTED",
        f"pack {locator.name!r} uses source.resource, which requires a pre-resolved pack bundle contract",
    )


def _local_pack_root(project_root: Path, locator: PackLocator) -> Path:
    assert locator.local is not None
    project_root = project_root.resolve()
    root = (project_root / locator.local).resolve(strict=True)
    try:
        root.relative_to(project_root)
    except ValueError as exc:
        raise ProjectError(
            "CLI_PACK_ESCAPE", f"pack {locator.name!r} escapes project root"
        ) from exc
    if not root.is_dir():
        raise ProjectError(
            "CLI_PACK_TYPE", f"pack {locator.name!r} source is not a directory"
        )
    return root


def _bundle_git_pack(locator: PackLocator) -> PackBundleUpload:
    assert locator.git is not None
    assert locator.ref is not None
    _git_argument(locator.git, "repository URL")
    _git_argument(locator.ref, "ref")
    with TemporaryDirectory(prefix="dryv-pack-") as temporary:
        checkout = Path(temporary) / "checkout"
        _run_git(("init", "--quiet", str(checkout)), locator.name)
        _run_git(
            ("-C", str(checkout), "remote", "add", "origin", locator.git),
            locator.name,
        )
        _run_git(
            (
                "-C",
                str(checkout),
                "fetch",
                "--quiet",
                "--depth=1",
                "--no-tags",
                "origin",
                locator.ref,
            ),
            locator.name,
        )
        _run_git(
            ("-C", str(checkout), "checkout", "--quiet", "--detach", "--force", "FETCH_HEAD"),
            locator.name,
        )
        root = checkout if locator.path is None else checkout.joinpath(*PurePosixPath(locator.path).parts)
        root = root.resolve(strict=True)
        try:
            root.relative_to(checkout.resolve())
        except ValueError as exc:
            raise ProjectError(
                "CLI_PACK_GIT_PATH",
                f"Git pack {locator.name!r} source.path escapes the checkout",
            ) from exc
        if not root.is_dir():
            raise ProjectError(
                "CLI_PACK_GIT_PATH",
                f"Git pack {locator.name!r} source.path is not a directory",
            )
        return _bundle_pack(root, locator.name)


def _run_git(arguments: tuple[str, ...], pack_name: str) -> None:
    try:
        completed = subprocess.run(
            ("git", *arguments),
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=_GIT_TIMEOUT_SECONDS,
        )
    except FileNotFoundError as exc:
        raise ProjectError(
            "CLI_GIT_MISSING",
            f"Git is required to resolve pack {pack_name!r} but was not found",
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ProjectError(
            "CLI_GIT_TIMEOUT",
            f"Git timed out while resolving pack {pack_name!r}",
        ) from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "Git command failed"
        raise ProjectError(
            "CLI_GIT_FAILED", f"could not resolve Git pack {pack_name!r}: {detail}"
        )


def _git_argument(value: str, label: str) -> None:
    if (
        not value
        or value.strip() != value
        or value.startswith("-")
        or "\x00" in value
        or "\n" in value
        or "\r" in value
    ):
        raise ProjectError("CLI_GIT_ARGUMENT", f"Git pack {label} is invalid")


def _bundle_pack(root: Path, instance_name: str) -> PackBundleUpload:
    root = root.resolve(strict=True)
    manifests = tuple(root / name for name in _MANIFEST_NAMES if (root / name).exists())
    if len(manifests) != 1:
        raise ProjectError(
            "CLI_PACK_MANIFEST",
            f"pack {instance_name!r} must contain exactly one of {', '.join(_MANIFEST_NAMES)}",
        )
    manifest_path = manifests[0]
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ProjectError(
            "CLI_PACK_MANIFEST",
            f"pack {instance_name!r} manifest must be a regular non-symlink file",
        )
    manifest = upload_bytes(
        f"resource://pack/{instance_name}/manifest",
        (
            "application/dryv-pack+json"
            if manifest_path.suffix == ".json"
            else "application/dryv-pack+yaml"
        ),
        manifest_path.read_bytes(),
    )
    resources: list[PackResourceUpload] = []
    for path in _pack_files(root):
        if path == manifest_path:
            continue
        relative = path.relative_to(root).as_posix()
        _safe_relative(relative)
        resources.append(
            PackResourceUpload(
                relative,
                upload_bytes(
                    f"resource://pack/{instance_name}/{relative}",
                    guess_media_type(path),
                    path.read_bytes(),
                ),
            )
        )
    return PackBundleUpload(instance_name, manifest, tuple(resources))


def _pack_files(root: Path) -> tuple[Path, ...]:
    root = root.resolve(strict=True)
    result: list[Path] = []
    for current, directories, files in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        retained: list[str] = []
        for name in sorted(directories):
            child = current_path / name
            if name == ".git":
                continue
            if child.is_symlink():
                raise ProjectError(
                    "CLI_PACK_SYMLINK",
                    f"pack directories must not be symlinks: {child.relative_to(root).as_posix()!r}",
                )
            retained.append(name)
        directories[:] = retained
        for name in sorted(files):
            if name == ".git":
                continue
            path = current_path / name
            if path.is_symlink():
                raise ProjectError(
                    "CLI_PACK_SYMLINK",
                    f"pack resources must not be symlinks: {path.relative_to(root).as_posix()!r}",
                )
            resolved = path.resolve(strict=True)
            try:
                resolved.relative_to(root)
            except ValueError as exc:
                raise ProjectError(
                    "CLI_PACK_ESCAPE",
                    f"pack resource escapes pack root: {path.relative_to(root).as_posix()!r}",
                ) from exc
            if not resolved.is_file():
                raise ProjectError(
                    "CLI_PACK_TYPE",
                    f"pack resource is not a regular file: {path.relative_to(root).as_posix()!r}",
                )
            result.append(resolved)
    return tuple(sorted(result, key=lambda item: item.relative_to(root).as_posix()))


def _safe_relative(value: str) -> None:
    path = PurePosixPath(value)
    if (
        not value
        or value.startswith("/")
        or "\\" in value
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise ProjectError("CLI_PACK_PATH", f"unsafe pack resource path {value!r}")


__all__ = ["ResolvedPack", "resolve_packs"]
