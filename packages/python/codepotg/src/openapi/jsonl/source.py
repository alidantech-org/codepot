from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from collections.abc import Callable, Mapping
from dataclasses import replace
from pathlib import Path
from typing import Any

import yaml

from .compiler import compile_openapi_jsonl
from .errors import JsonlInputError
from .models import (
    HotIndexLimits,
    JsonlCompileResult,
    JsonlLimits,
    JsonlManifest,
    JsonlQueueLimits,
)

SourceProgressSink = Callable[[Mapping[str, Any]], None]
_YAML_SUFFIXES = frozenset({".yaml", ".yml"})
_JSON_SUFFIXES = frozenset({".json"})
_YAML_WARNING = (
    "YAML input is supported through a compatibility conversion. "
    "Use OpenAPI JSON for true streaming, lower peak memory, and predictable performance."
)
_CONVERTED_SOURCE_NAME = "source.json"
_COPY_BUFFER_BYTES = 4 * 1024 * 1024


def compile_openapi_source_jsonl(
    source: str | Path,
    cache_dir: str | Path,
    *,
    limits: JsonlLimits | None = None,
    hot_limits: HotIndexLimits | None = None,
    queue_limits: JsonlQueueLimits | None = None,
    reuse_unchanged: bool = True,
    progress: SourceProgressSink | None = None,
) -> JsonlCompileResult:
    """Compile JSON directly or YAML through a bounded compatibility adapter."""

    source_path = Path(source)
    target = Path(cache_dir)
    suffix = source_path.suffix.lower()
    if suffix in _JSON_SUFFIXES:
        return compile_openapi_jsonl(
            source_path,
            target,
            limits=limits,
            hot_limits=hot_limits,
            queue_limits=queue_limits,
            reuse_unchanged=reuse_unchanged,
            progress=progress,
        )
    if suffix not in _YAML_SUFFIXES:
        raise JsonlInputError(
            f"Unsupported OpenAPI source extension '{suffix}'. Use .json, .yaml, or .yml."
        )
    if not source_path.is_file():
        raise JsonlInputError(f"OpenAPI input does not exist or is not a file: {source_path}")

    if progress is not None:
        progress(
            {
                "stage": "input",
                "status": "compatibility",
                "format": "yaml",
                "warning": _YAML_WARNING,
                "file": source_path.name,
            }
        )

    original_hash, original_size = _hash_file(source_path)
    converted_source = target / _CONVERTED_SOURCE_NAME
    if reuse_unchanged and _can_reuse_yaml_conversion(
        target / "manifest.json",
        converted_source,
        original_hash=original_hash,
        original_size=original_size,
    ):
        temporary = _copy_converted_source(converted_source, target.parent, target.name)
        try:
            result = compile_openapi_jsonl(
                temporary,
                target,
                limits=limits,
                hot_limits=hot_limits,
                queue_limits=queue_limits,
                reuse_unchanged=True,
                progress=progress,
            )
            if result.reused:
                return replace(result, compatibility_path=converted_source)
            return _finalize_yaml_result(
                result,
                temporary=temporary,
                source_path=source_path,
                original_hash=original_hash,
                original_size=original_size,
            )
        finally:
            temporary.unlink(missing_ok=True)

    try:
        with source_path.open("r", encoding="utf-8") as stream:
            raw = yaml.safe_load(stream)
    except (OSError, yaml.YAMLError) as exc:
        raise JsonlInputError(f"Unable to load OpenAPI YAML: {source_path}") from exc
    if not isinstance(raw, dict):
        raise JsonlInputError("OpenAPI YAML root must be an object")

    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}-source-",
        suffix=".json",
        dir=target.parent,
        text=True,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(
                raw,
                stream,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            stream.flush()
            os.fsync(stream.fileno())
        del raw

        result = compile_openapi_jsonl(
            temporary,
            target,
            limits=limits,
            hot_limits=hot_limits,
            queue_limits=queue_limits,
            reuse_unchanged=False,
            progress=progress,
        )
        return _finalize_yaml_result(
            result,
            temporary=temporary,
            source_path=source_path,
            original_hash=original_hash,
            original_size=original_size,
        )
    finally:
        temporary.unlink(missing_ok=True)


def yaml_compatibility_warning() -> str:
    """Return the stable author-facing YAML compatibility warning."""

    return _YAML_WARNING


def _copy_converted_source(source: Path, parent: Path, cache_name: str) -> Path:
    parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{cache_name}-source-rebuild-",
        suffix=".json",
        dir=parent,
    )
    temporary = Path(temporary_name)
    try:
        with source.open("rb") as input_stream, os.fdopen(descriptor, "wb") as output_stream:
            shutil.copyfileobj(input_stream, output_stream, length=_COPY_BUFFER_BYTES)
            output_stream.flush()
            os.fsync(output_stream.fileno())
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return temporary


def _finalize_yaml_result(
    result: JsonlCompileResult,
    *,
    temporary: Path,
    source_path: Path,
    original_hash: str,
    original_size: int,
) -> JsonlCompileResult:
    converted_source = result.cache_dir / _CONVERTED_SOURCE_NAME
    os.replace(temporary, converted_source)
    source_meta = {
        **dict(result.manifest.source),
        "path": source_path.name,
        "format": "yaml",
        "compiledFormat": "json",
        "compatibilityPath": _CONVERTED_SOURCE_NAME,
        "originalSize": original_size,
        "originalSha256": original_hash,
        "compatibilityWarning": _YAML_WARNING,
    }
    manifest = replace(result.manifest, source=source_meta)
    _write_manifest(result.cache_dir / "manifest.json", manifest)
    return replace(
        result,
        manifest=manifest,
        compatibility_path=converted_source,
    )


def _can_reuse_yaml_conversion(
    manifest_path: Path,
    converted_source: Path,
    *,
    original_hash: str,
    original_size: int,
) -> bool:
    if not converted_source.is_file() or not manifest_path.is_file():
        return False
    try:
        with manifest_path.open("r", encoding="utf-8") as stream:
            manifest = json.load(stream)
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(manifest, Mapping):
        return False
    source = manifest.get("source")
    return bool(
        isinstance(source, Mapping)
        and source.get("format") == "yaml"
        and source.get("originalSha256") == original_hash
        and source.get("originalSize") == original_size
        and source.get("compatibilityPath") == _CONVERTED_SOURCE_NAME
        and source.get("sha256") == _hash_file(converted_source)[0]
        and source.get("size") == converted_source.stat().st_size
    )


def _hash_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            size += len(chunk)
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}", size


def _write_manifest(path: Path, manifest: JsonlManifest) -> None:
    encoded = json.dumps(
        manifest.to_json(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        temporary.write_bytes(encoded + b"\n")
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
