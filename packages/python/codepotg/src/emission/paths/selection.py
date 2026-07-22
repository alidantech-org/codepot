"""Folder recipe expansion for template paths."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from contracts.paths import PathConfig, PathFolder, PathSelectionMode
from emission.templates.path_expander import expand_template_parts
from emission.templates.resolver import resolve_variable

CONTEXT_FOLDER_NAME = "__path_folder_name"
CONTEXT_FOLDER_PARTS = "__path_folder_parts"


def expand_folder_contexts(
    base_context: Mapping[str, Any],
    folder_name: str,
    path_config: PathConfig,
) -> tuple[dict[str, Any], ...]:
    """Expand a folder recipe into render contexts with resolved folder parts."""
    folders = path_config.folder_by_name()

    if folder_name not in folders:
        raise KeyError(f"path folder not configured in paths.yaml: {folder_name}")

    folder = folders[folder_name]
    return _expand_one(dict(base_context), folder)


def _expand_one(
    context: dict[str, Any],
    folder: PathFolder,
) -> tuple[dict[str, Any], ...]:
    if folder.mode == PathSelectionMode.ONCE:
        selected = resolve_variable(context, folder.select) if folder.select else None
        return (_bind_context(context, folder, selected),)

    if not folder.select:
        raise ValueError(f"folder '{folder.name}' requires select unless mode is once")

    selected = resolve_variable(context, folder.select)

    if not isinstance(selected, (list, tuple)):
        raise TypeError(f"folder '{folder.name}' must resolve to a list/tuple")

    return tuple(_bind_context(context, folder, item) for item in selected)


def _bind_context(
    context: dict[str, Any],
    folder: PathFolder,
    item: Any,
) -> dict[str, Any]:
    bound = dict(context)
    bound[folder.alias] = item
    bound[CONTEXT_FOLDER_NAME] = folder.name
    bound[CONTEXT_FOLDER_PARTS] = expand_template_parts(folder.parts, bound)
    return bound
