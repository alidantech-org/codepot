from __future__ import annotations

import hashlib
import json
import os
import shutil
import uuid
from collections.abc import Callable, Mapping
from contextlib import suppress
from pathlib import Path, PurePosixPath
from typing import Any

from core.system_resources import tune_runtime

from .errors import JsonlCompilerError, JsonlInputError
from .hot_index import HotIndexRegistry
from .indexing import SectionWriter, classify_record, register_record_indexes
from .models import (
    ExtractedRecord,
    HotIndexLimits,
    JsonlCompileResult,
    JsonlLimits,
    JsonlManifest,
    JsonlQueueLimits,
    JsonlQueueStats,
    SectionManifest,
)
from .operation_indexing import register_additional_indexes
from .queueing import JsonlRecordPipeline, create_event_writer_factory
from .sqlite_index import SqliteIndexWriter
from .stream import stream_openapi_json

_CACHE_VERSION = 3
_INDEX_CATEGORIES = ("definitions", "mentions", "dependencies")
JsonlProgressSink = Callable[[Mapping[str, Any]], None]


def compile_openapi_jsonl(
    source: str | Path,
    cache_dir: str | Path,
    *,
    limits: JsonlLimits | None = None,
    hot_limits: HotIndexLimits | None = None,
    queue_limits: JsonlQueueLimits | None = None,
    reuse_unchanged: bool = True,
    progress: JsonlProgressSink | None = None,
) -> JsonlCompileResult:
    source_path = Path(source)
    target = Path(cache_dir)
    if source_path.suffix.lower() != ".json":
        raise JsonlInputError(
            "JSONL compilation is JSON-first. Convert YAML to JSON for faster, "
            "bounded extraction."
        )

    _notify(
        progress,
        stage="compiler",
        status="started",
        source=str(source_path),
        cache=str(target),
    )
    source_digest = _hash_file(source_path)
    source_size = source_path.stat().st_size
    tuning = tune_runtime(source_size)
    effective_hot_limits = hot_limits or HotIndexLimits(
        max_entries=tuning.hot_index_entries,
        max_bytes=tuning.hot_index_bytes,
    )
    effective_queue_limits = queue_limits or JsonlQueueLimits(
        max_records=tuning.jsonl_pending_records,
        max_pending_bytes=tuning.jsonl_pending_bytes,
        max_events=tuning.jsonl_event_queue,
        emit_record_events=_record_events_enabled(),
    )
    _notify(
        progress,
        stage="runtime",
        status="tuned",
        message=tuning.summary(),
        availableMemory=tuning.available_memory,
        sourceBytes=source_size,
    )

    existing = _read_manifest(target / "manifest.json") if reuse_unchanged else None
    if existing is not None and _can_reuse(existing, source_digest, source_size, target):
        manifest = _manifest_from_json(existing)
        _notify(
            progress,
            stage="compiler",
            status="reused",
            source=str(source_path),
            cache=str(target),
        )
        return JsonlCompileResult(
            cache_dir=target,
            manifest=manifest,
            hot_index=HotIndexRegistry(effective_hot_limits),
            reused=True,
            diagnostics=[tuning.summary()],
        )

    staging = target.with_name(f".{target.name}.staging-{uuid.uuid4().hex}")
    backup = target.with_name(f".{target.name}.backup-{uuid.uuid4().hex}")
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True, exist_ok=False)

    sections = SectionWriter(staging)
    indexes = SqliteIndexWriter(
        staging,
        cache_bytes=tuning.sqlite_cache_bytes,
        batch_size=max(2_000, tuning.jsonl_pending_records * 4),
    )
    hot_index = HotIndexRegistry(effective_hot_limits)
    counters = {"records": 0, "definitions": 0, "mentions": 0, "dependencies": 0}
    queue_stats = JsonlQueueStats()
    pipeline: JsonlRecordPipeline | None = None

    def process_record(record: ExtractedRecord) -> None:
        classification = classify_record(record)
        location = sections.write(record, classification)
        definitions, mentions, dependencies = register_record_indexes(
            record,
            classification,
            location,
            indexes=indexes,
            hot_index=hot_index,
        )
        extra_mentions, extra_dependencies = register_additional_indexes(
            record,
            classification,
            location,
            indexes=indexes,
        )
        counters["records"] += 1
        counters["definitions"] += definitions
        counters["mentions"] += mentions + extra_mentions
        counters["dependencies"] += dependencies + extra_dependencies
        _notify(
            progress,
            stage="record",
            status="written",
            section=record.section,
            name=record.name,
            file=location.file,
            records=counters["records"],
        )

    try:
        pipeline = JsonlRecordPipeline(
            process_record,
            limits=effective_queue_limits,
            event_writer_factory=create_event_writer_factory(staging),
        )
        pipeline.start()
        summary = stream_openapi_json(
            source_path,
            on_record=pipeline.submit,
            limits=limits,
        )
        event_manifest, queue_stats = pipeline.close()
        section_manifests = sections.close()
        indexes.close()
        index_manifest = indexes.manifest()

        for section, section_manifest in sorted(section_manifests.items()):
            _notify(
                progress,
                stage="section",
                status="written",
                section=section,
                file=section_manifest.file,
                records=section_manifest.count,
                bytes=section_manifest.bytes,
            )

        for category, raw_index in sorted(index_manifest.items()):
            _notify(
                progress,
                stage="index",
                status="written",
                category=category,
                backend=raw_index["backend"],
                database=raw_index["database"],
                records=raw_index["records"],
            )

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
            indexes=index_manifest,
            events=event_manifest,
        )
        _write_manifest(staging / "manifest.json", manifest)
        _replace_directory(staging, target, backup)
    except Exception:
        if pipeline is not None:
            pipeline.cancel()
            with suppress(Exception):
                pipeline.close()
        with suppress(Exception):
            sections.close()
        with suppress(Exception):
            indexes.close()
        shutil.rmtree(staging, ignore_errors=True)
        _notify(
            progress,
            stage="compiler",
            status="failed",
            source=str(source_path),
            cache=str(target),
        )
        raise

    _notify(
        progress,
        stage="compiler",
        status="completed",
        source=str(source_path),
        cache=str(target),
        records=counters["records"],
    )
    return JsonlCompileResult(
        cache_dir=target,
        manifest=manifest,
        hot_index=hot_index,
        reused=False,
        records_written=counters["records"],
        definitions_written=counters["definitions"],
        mentions_written=counters["mentions"],
        dependencies_written=counters["dependencies"],
        queue_stats=queue_stats,
        diagnostics=[tuning.summary()],
    )


def _notify(
    progress: JsonlProgressSink | None,
    *,
    stage: str,
    status: str,
    **details: Any,
) -> None:
    if progress is None:
        return
    progress({"stage": stage, "status": status, **details})


def _hash_file(path: Path) -> str:
    if not path.exists():
        raise JsonlInputError(f"OpenAPI input does not exist: {path}")
    if not path.is_file():
        raise JsonlInputError(f"OpenAPI input is not a file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(4 * 1024 * 1024):
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
    indexes = manifest.get("indexes")
    events = manifest.get("events")
    if not (
        manifest.get("version") == _CACHE_VERSION
        and isinstance(source, Mapping)
        and source.get("sha256") == digest
        and source.get("size") == size
        and isinstance(sections, Mapping)
        and isinstance(indexes, Mapping)
        and isinstance(events, Mapping)
    ):
        return False

    for raw_section in sections.values():
        if not isinstance(raw_section, Mapping):
            return False
        relative = raw_section.get("file")
        if not isinstance(relative, str) or not _cache_file_exists(target, relative):
            return False

    event_file = events.get("file")
    if not isinstance(event_file, str) or not _cache_file_exists(target, event_file):
        return False

    databases: set[str] = set()
    for category in _INDEX_CATEGORIES:
        raw_index = indexes.get(category)
        if not isinstance(raw_index, Mapping):
            return False
        database = raw_index.get("database")
        if not isinstance(database, str):
            return False
        databases.add(database)
    return all(_cache_file_exists(target, database) for database in databases)


def _cache_file_exists(root: Path, relative: str) -> bool:
    if "\\" in relative:
        return False
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts:
        return False
    return (root / Path(*pure.parts)).is_file()


def _manifest_from_json(value: Mapping[str, Any]) -> JsonlManifest:
    raw_sections = value.get("sections")
    if not isinstance(raw_sections, Mapping):
        raise JsonlCompilerError("Existing JSONL manifest has invalid sections")
    sections: dict[str, SectionManifest] = {}
    for key, raw in raw_sections.items():
        if not isinstance(raw, Mapping):
            raise JsonlCompilerError("Existing JSONL manifest has invalid section metadata")
        sections[str(key)] = SectionManifest.from_json(raw)
    source = value.get("source")
    root = value.get("root")
    indexes = value.get("indexes")
    raw_events = value.get("events")
    if not (
        isinstance(source, Mapping)
        and isinstance(root, Mapping)
        and isinstance(indexes, Mapping)
        and isinstance(raw_events, Mapping)
    ):
        raise JsonlCompilerError("Existing JSONL manifest is incomplete")
    return JsonlManifest(
        version=int(value["version"]),
        source=source,
        root=root,
        sections=sections,
        indexes=indexes,
        events=SectionManifest.from_json(raw_events),
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


def _record_events_enabled() -> bool:
    return os.getenv("CODEPOTG_JSONL_RECORD_EVENTS", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
