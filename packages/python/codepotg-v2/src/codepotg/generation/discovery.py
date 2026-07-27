from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

from pathspec import PathSpec

from codepotg.config import PackManifest
from codepotg.runtime.plugins import PluginLoadError, RuntimePlugins

from .manifest_validation import (
    validate_pack_compatibility,
    validate_selection_graph,
)
from .models import DiscoveredPackFile, PackFileKind

_SELECTION_FOLDER = re.compile(r"^\{([A-Za-z][A-Za-z0-9_-]*)\}$")


class PackDiscoveryError(ValueError):
    def __init__(self, code: str, message: str, *, path: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.path = path
        self.message = message


def discover_pack_files(
    pack_root: str | Path,
    manifest: PackManifest,
    plugins: RuntimePlugins,
) -> tuple[DiscoveredPackFile, ...]:
    validate_pack_compatibility(manifest)
    validate_selection_graph(manifest)
    if manifest.commands:
        raise PackDiscoveryError(
            "CMD_APPROVAL_REQUIRED",
            "pack-owned commands require the separate approved command runtime",
            path="CodepotgPack.yaml#commands",
        )

    root = Path(pack_root).resolve(strict=True)
    templates = (root / "templates").resolve(strict=True)
    _require_contained(templates, root, "PACK_TEMPLATES_ESCAPE")
    if not templates.is_dir():
        raise PackDiscoveryError(
            "PACK_TEMPLATES_MISSING",
            "pack root must contain a templates directory",
            path=templates.as_posix(),
        )

    include_spec = PathSpec.from_lines("gitwildmatch", manifest.include)
    exclude_spec = PathSpec.from_lines("gitwildmatch", manifest.exclude)
    root_ignore = _root_ignore(root)

    discovered: list[DiscoveredPackFile] = []
    for candidate in sorted(templates.rglob("*"), key=lambda item: item.as_posix()):
        if candidate.name == ".gitignore" or not candidate.is_file():
            continue
        canonical = candidate.resolve(strict=True)
        _require_contained(canonical, templates, "PACK_FILE_ESCAPE")
        relative = canonical.relative_to(templates).as_posix()
        pack_relative = canonical.relative_to(root).as_posix()
        if not include_spec.match_file(relative):
            continue
        if exclude_spec.match_file(relative) or (
            root_ignore is not None and root_ignore.match_file(pack_relative)
        ):
            continue

        parts = PurePosixPath(relative).parts
        selection_key = _selection_key(parts, manifest)
        partial = bool(parts and parts[0] == "_partials")
        content = canonical.read_bytes()

        try:
            engine, engine_suffix = plugins.engine_for_path(relative)
        except PluginLoadError:
            if partial:
                raise PackDiscoveryError(
                    "PACK_PARTIAL_ENGINE_MISSING",
                    "partial files must use a recognized template-engine suffix",
                    path=relative,
                )
            discovered.append(
                DiscoveredPackFile(
                    pack_path=relative,
                    kind=PackFileKind.STATIC,
                    content=content,
                    selection_key=selection_key,
                )
            )
            continue

        target_path = relative[: -len(engine_suffix)]
        target_id: str | None = None
        target_suffix: str | None = None
        try:
            _, target_id, target_suffix = plugins.target_for_path(target_path)
        except PluginLoadError:
            pass

        discovered.append(
            DiscoveredPackFile(
                pack_path=relative,
                kind=PackFileKind.PARTIAL if partial else PackFileKind.TEMPLATE,
                content=content,
                engine_id=engine.plugin.id,
                engine_suffix=engine_suffix,
                target_id=target_id,
                target_suffix=target_suffix,
                selection_key=selection_key,
            )
        )

    return tuple(discovered)


def _selection_key(parts: tuple[str, ...], manifest: PackManifest) -> str | None:
    keys = tuple(
        match.group(1)
        for part in parts
        if (match := _SELECTION_FOLDER.fullmatch(part)) is not None
    )
    if len(keys) > 1:
        raise PackDiscoveryError(
            "PACK_SELECTION_FOLDER_NESTED",
            "one template path may contain at most one selection folder",
            path="/".join(parts),
        )
    if not keys:
        return None
    key = keys[0]
    if key != "root" and manifest.selection(key) is None:
        raise PackDiscoveryError(
            "PACK_SELECTION_UNKNOWN",
            f"template path references unknown selection {key!r}",
            path="/".join(parts),
        )
    return key


def _root_ignore(root: Path) -> PathSpec | None:
    ignore = root / ".gitignore"
    if not ignore.is_file():
        return None
    try:
        lines = ignore.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise PackDiscoveryError(
            "PACK_IGNORE_READ_FAILED",
            "pack-root .gitignore could not be read as UTF-8",
            path=ignore.as_posix(),
        ) from exc
    return PathSpec.from_lines("gitwildmatch", lines)


def _require_contained(path: Path, root: Path, code: str) -> None:
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise PackDiscoveryError(
            code,
            "pack discovery path escapes the authorized pack root",
            path=path.as_posix(),
        ) from exc
