"""Headless OpenAPI reconstruction from SQLite handles and JSONL raw records."""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import JsonlSelectionError
from .indexing import extract_ref_mentions
from .models import RecordLocation
from .selections import JsonlSelectionStore, SelectionHandle


@dataclass(frozen=True, slots=True)
class SelectedDocumentResult:
    """One reduced OpenAPI document and its bounded source-read statistics."""

    document: dict[str, Any]
    selections: tuple[str, ...]
    records_loaded: int
    dependency_records_loaded: int
    unresolved_refs: tuple[str, ...]


def build_selected_openapi_document(
    cache_dir: str | Path,
    selections: tuple[str, ...] | list[str] | set[str],
    *,
    max_records: int = 100_000,
    max_dependency_depth: int = 64,
) -> SelectedDocumentResult:
    """Load selected records and only their reachable internal dependencies.

    Selection discovery is SQLite-only. JSONL is read by exact offset only when a
    selected record or one of its internal ``$ref`` dependencies is materialized.
    Operation selections load their parent path record so path-level parameters and
    ``x-codegen`` resource metadata are preserved.
    """
    if max_records < 1:
        raise ValueError("max_records must be at least 1")
    if max_dependency_depth < 0:
        raise ValueError("max_dependency_depth must be non-negative")

    cache = Path(cache_dir)
    manifest = _read_manifest(cache / "manifest.json")
    root = manifest.get("root")
    if not isinstance(root, dict):
        raise JsonlSelectionError("JSONL manifest root metadata is missing")

    requested = tuple(sorted({str(value) for value in selections if str(value)}))
    document: dict[str, Any] = dict(root)
    document["paths"] = {}
    store = JsonlSelectionStore(cache)
    queue: deque[tuple[SelectionHandle, int, bool]] = deque()
    seen_locations: set[str] = set()
    unresolved: set[str] = set()
    selected_keys: set[str] = set()
    records_loaded = 0
    dependency_records_loaded = 0

    try:
        for selection in requested:
            for handle in store.iter_handles(selection):
                selected_keys.add(handle.key)
                queue.append((_path_parent_handle(store, handle), 0, False))

        while queue:
            handle, depth, is_dependency = queue.popleft()
            identity = handle.cache_key
            if identity in seen_locations:
                continue
            if len(seen_locations) >= max_records:
                raise JsonlSelectionError(
                    f"Selected document exceeds record limit {max_records}"
                )
            seen_locations.add(identity)

            record = store.load(handle)
            records_loaded += 1
            if is_dependency:
                dependency_records_loaded += 1
            _insert_record(document, handle.location, record.raw)

            if depth >= max_dependency_depth:
                continue
            for ref, _purpose in extract_ref_mentions(record.raw):
                location = store.index_store.get_by_ref(ref)
                if location is None:
                    if ref.startswith("#/"):
                        unresolved.add(ref)
                    continue
                dependency_handle = SelectionHandle(
                    selection="dependency",
                    key=location.key,
                    ref=location.ref,
                    kind=location.kind,
                    resources=location.resources,
                    location=location,
                )
                queue.append(
                    (
                        _path_parent_handle(store, dependency_handle),
                        depth + 1,
                        dependency_handle.key not in selected_keys,
                    )
                )
    finally:
        store.close()

    return SelectedDocumentResult(
        document=document,
        selections=requested,
        records_loaded=records_loaded,
        dependency_records_loaded=dependency_records_loaded,
        unresolved_refs=tuple(sorted(unresolved)),
    )


def _path_parent_handle(
    store: JsonlSelectionStore,
    handle: SelectionHandle,
) -> SelectionHandle:
    if handle.kind != "operation" or not handle.key.startswith("operation:"):
        return handle
    try:
        _prefix, _method, path = handle.key.split(":", 2)
    except ValueError:
        return handle
    location = store.index_store.get_by_key(f"path:{path}")
    if location is None:
        return handle
    return SelectionHandle(
        selection=handle.selection,
        key=location.key,
        ref=location.ref,
        kind=location.kind,
        resources=location.resources,
        location=location,
    )


def _insert_record(
    document: dict[str, Any],
    location: RecordLocation,
    raw: Any,
) -> None:
    section = location.section
    if section == "paths":
        path = _record_name(location, prefix="path")
        paths = document.setdefault("paths", {})
        if not isinstance(paths, dict):
            raise JsonlSelectionError("Selected document paths root is not an object")
        paths[path] = raw
        return

    group, separator, collection = section.partition("/")
    if not separator or group not in {"components", "x-codegen"}:
        raise JsonlSelectionError(f"Unsupported selected JSONL section: {section}")
    name = _record_name(location)
    group_value = document.setdefault(group, {})
    if not isinstance(group_value, dict):
        raise JsonlSelectionError(f"Selected document {group} root is not an object")
    collection_value = group_value.setdefault(collection, {})
    if not isinstance(collection_value, dict):
        raise JsonlSelectionError(
            f"Selected document section {section} is not an object"
        )
    collection_value[name] = raw


def _record_name(location: RecordLocation, *, prefix: str | None = None) -> str:
    key_prefix, separator, key_name = location.key.partition(":")
    if separator and (prefix is None or key_prefix == prefix):
        return key_name
    if location.ref:
        return _pointer_unescape(location.ref.rsplit("/", 1)[-1])
    raise JsonlSelectionError(f"Selected record has no stable name: {location.key}")


def _pointer_unescape(value: str) -> str:
    return value.replace("~1", "/").replace("~0", "~")


def _read_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError) as exc:
        raise JsonlSelectionError(f"Unable to read JSONL manifest: {path}") from exc
    if not isinstance(value, dict):
        raise JsonlSelectionError("JSONL manifest root must be an object")
    return value
