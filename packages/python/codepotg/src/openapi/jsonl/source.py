from __future__ import annotations

import hashlib
import json
import os
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
    """Compile JSON directly or YAML through a deterministic JSON adapter."""

    source_path = Path(source)
    suffix = source_path.suffix.lower()
    if suffix in _JSON_SUFFIXES:
        return compile_openapi_jsonl(
            source_path,
            cache_dir,
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

    try:
        with source_path.open("r", encoding="utf-8") as stream:
            raw = yaml.safe_load(stream)
    except (OSError, yaml.YAMLError) as exc:
        raise JsonlInputError(f"Unable to load OpenAPI YAML: {source_path}") from exc
    if not isinstance(raw, dict):
        raise JsonlInputError("OpenAPI YAML root must be an object")

    encoded = json.dumps(
        raw,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    original_bytes = source_path.read_bytes()
    original_hash = f"sha256:{hashlib.sha256(original_bytes).hexdigest()}"

    with tempfile.TemporaryDirectory(prefix="codepotg-yaml-json-") as directory:
        converted = Path(directory) / "openapi.json"
        converted.write_bytes(encoded)
        result = compile_openapi_jsonl(
            converted,
            cache_dir,
            limits=limits,
            hot_limits=hot_limits,
            queue_limits=queue_limits,
            reuse_unchanged=reuse_unchanged,
            progress=progress,
        )

    source_meta = {
        **dict(result.manifest.source),
        "path": source_path.name,
        "format": "yaml",
        "compiledFormat": "json",
        "originalSize": len(original_bytes),
        "originalSha256": original_hash,
        "compatibilityWarning": _YAML_WARNING,
    }
    manifest = replace(result.manifest, source=source_meta)
    _write_manifest(result.cache_dir / "manifest.json", manifest)
    return replace(result, manifest=manifest)


def yaml_compatibility_warning() -> str:
    """Return the stable author-facing YAML compatibility warning."""

    return _YAML_WARNING


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
