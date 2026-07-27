from __future__ import annotations

import fnmatch
import re
from pathlib import Path, PurePosixPath

from codepotg.config import PackManifest
from codepotg.runtime.plugins import PluginLoadError, RuntimePlugins

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
    root = Path(pack_root)
    templates = root / "templates"
    if not templates.is_dir():
        raise PackDiscoveryError(
            "PACK_TEMPLATES_MISSING",
            "pack root must contain a templates directory",
            path=templates.as_posix(),
        )

    discovered: list[DiscoveredPackFile] = []
    for candidate in sorted(templates.rglob("*"), key=lambda item: item.as_posix()):
        if not candidate.is_file():
            continue
        relative = candidate.relative_to(templates).as_posix()
        if not _included(relative, manifest.include, manifest.exclude):
            continue
        parts = PurePosixPath(relative).parts
        selection_key = _selection_key(parts, manifest)
        partial = bool(parts and parts[0] == "_partials")
        content = candidate.read_bytes()

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


def _included(path: str, include: tuple[str, ...], exclude: tuple[str, ...]) -> bool:
    return any(_match(path, pattern) for pattern in include) and not any(
        _match(path, pattern) for pattern in exclude
    )


def _match(path: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(path, pattern) or (
        pattern.startswith("**/") and fnmatch.fnmatchcase(path, pattern[3:])
    )
