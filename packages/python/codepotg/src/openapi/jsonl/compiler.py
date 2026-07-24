from __future__ import annotations

import hashlib
import json
import os
import shutil
import uuid
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .errors import JsonlCompilerError, JsonlInputError
from .hot_index import HotIndexRegistry
from .indexing import (
    SectionWriter,
    ShardedIndexWriter,
    classify_record,
    register_record_indexes,
)
from .models import (
    HotIndexLimits,
    JsonlCompileResult,
    JsonlLimits,
    JsonlManifest,
    SectionManifest,
)
from .stream import stream_openapi_json

_CACHE_VERSION = 1


def compile_openapi_jsonl(
    source: str | Path,
    cache_dir: str | Path,
    *,
    limits: JsonlLimits | None = None,
    hot_limits: HotIndexLimits | None = None,
    reuse_unchanged: bool = True,
) -> JsonlCompileResult:
    source_path = Path(source)
    target = Path(cache_dir)
    if source_path.suffix.lower() != ".json":
        raise JsonlInputError(
            "JSONL compilation is JSON-first. Convert YAML to JSON for faster, "
            "bounded extraction."
        )

    source_digest = _hash_file(source_path)
    source_size = source_path.stat().st_size
    existing = _read_manifest(target / "manifest.json") if reuse_unchanged else None
    if existing is not None and _can_reuse(existing, source_digest, source_size, target):
        manifest = _manifest_from_json(existing)
        return JsonlCompileResult(
            cache_dir=target,
            manifest=manifest,
            hot_index=HotIndexRegistry(hot_limits),
            reused=True,
        )

    staging = target.with_name(f".{target.name}.staging-{uuid.uuid4().hex}")
    backup = target.with_name(f".{target.name}.backup-{uuid.uuid4().hex}")
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True, exist_ok=False)

    sections = SectionWriter(staging)
    indexes = ShardedIndexWriter(staging)
    hot_index = HotIndexRegistry(hot_limits)
    counters = {"records": 0, "definitions": 0, "mentions": 0, "dependencies": 0}

    def on_record(record: Any) -> None:
        classification = classify_record(record)
        location = sections.write(record, classification)
        definitions, mentions, dependencies = register_record_indexes(
            record,
            classification,
            location,
            indexes=indexes,
            hot_index=hot_index,
        )
        counters["records"] += 1
        counters["definitions"] += definitions
        counters["mentions"] += mentions
        counters["dependencies"] += dependencies

    try:
        summary = stream_openapi_json(source_path, on_record=on_record, limits=limits)
        section_manifests = sections.close()
        indexes.close()
        manifest = JsonlManifest(
            version=_CACHE_VERSION,
            source={
                "path": source_path.name,
                "format": "json",
                "size": source_size,
                "sha256": source_digest,
            },
            root=summary.root,
            sections=section_manifests,
            indexes=indexes.manifest(),
        )
        _write_manifest(staging / "manifest.json", manifest)
        _replace_directory(staging, target, backup)
    except Exception:
        try:
            sections.close()
        except Exception:
            pass
        try:
            indexes.close()
        except Exception:
            pass
        shutil.rmtree(staging, ignore_errors=True)
        raise

    return JsonlCompileResult(
        cache_dir=target,
        manifest=manifest,
        hot_index=hot_index,
        reused=False,
        records_written=counters["records"],
        definitions_written=counters["definitions"],
        mentions_written=counters["mentions"],
        dependencies_written=counters["dependencies"],
    )


def _hash_file(path: Path) -> str:
    if not path.exists():
        raise JsonlInputError(f"OpenAPI input does not exist: {path}")
    if not path.is_file():
        raise JsonlInputError(f"OpenAPI input is not a file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _write_manifest(path: Path, manifest: JsonlManifest) -> None:
    encoded = json.dumps(
        manifest.to_json(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    temp = path.with_suffix(".json.tmp")
    temp.write_bytes(encoded + b"\n")
    os.replace(temp, path)


def _read_manifest(path: Path) -> Mapping[str, Any] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, Mapping) else None


def _can_reuse(
    manifest: Mapping[str, Any],
    digest: str,
    size: int,
    target: Path,
) -> bool:
    source = manifest.get("source")
    sections = manifest.get("sections")
    if not (
        manifest.get("version") == _CACHE_VERSION
        and isinstance(source, Mapping)
        and source.get("sha256") == digest
        and source.get("size") == size
        and isinstance(sections, Mapping)
    ):
        return False
    for raw_section in sections.values():
        if not isinstance(raw_section, Mapping):
            return False
        relative = raw_section.get("file")
        if not isinstance(relative, str) or not (target / Path(relative)).is_file():
            return False
    return True


def _manifest_from_json(value: Mapping[str, Any]) -> JsonlManifest:
    raw_sections = value.get("sections")
    if not isinstance(raw_sections, Mapping):
        raise JsonlCompilerError("Existing JSONL manifest has invalid sections")
    sections: dict[str, SectionManifest] = {}
    for key, raw in raw_sections.items():
        if not isinstance(raw, Mapping):
            raise JsonlCompilerError("Existing JSONL manifest has invalid section metadata")
        sections[str(key)] = SectionManifest(
            file=str(raw["file"]),
            count=int(raw["count"]),
            bytes=int(raw["bytes"]),
            sha256=str(raw["sha256"]),
        )
    source = value.get("source")
    root = value.get("root")
    indexes = value.get("indexes")
    if not (
        isinstance(source, Mapping)
        and isinstance(root, Mapping)
        and isinstance(indexes, Mapping)
    ):
        raise JsonlCompilerError("Existing JSONL manifest is incomplete")
    return JsonlManifest(
        version=int(value["version"]),
        source=source,
        root=root,
        sections=sections,
        indexes=indexes,
    )


def _replace_directory(staging: Path, target: Path, backup: Path) -> None:
    shutil.rmtree(backup, ignore_errors=True)
    moved_existing = False
    try:
        if target.exists():
            os.replace(target, backup)
            moved_existing = True
        os.replace(staging, target)
    except Exception:
        if moved_existing and backup.exists() and not target.exists():
            os.replace(backup, target)
        raise
    finally:
        shutil.rmtree(backup, ignore_errors=True)
