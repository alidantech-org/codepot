"""Application workflow for user-visible indexed JSONL compilation."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

from app.models import JsonlInput, JsonlOutput, RuntimeEvent
from openapi.jsonl import compile_openapi_jsonl


def run_jsonl(request: JsonlInput) -> JsonlOutput:
    """Compile OpenAPI JSON into a visible indexed JSONL cache."""
    seen_files: set[str] = set()

    def progress(event: Mapping[str, Any]) -> None:
        stage = str(event.get("stage", "jsonl"))
        status = str(event.get("status", "progress"))
        relative = event.get("file")

        if stage == "record" and status == "written" and isinstance(relative, str):
            if relative in seen_files:
                return
            seen_files.add(relative)
            _notify(
                request,
                stage="jsonl_file_writing",
                message=f"Writing JSONL: {request.output_path / Path(relative)}",
                details={"file": relative, "section": event.get("section")},
            )
            return

        if stage == "section" and status == "written" and isinstance(relative, str):
            _notify(
                request,
                stage="jsonl_file_written",
                message=(
                    f"Wrote JSONL: {request.output_path / Path(relative)} "
                    f"({event.get('records', 0)} records)"
                ),
                details=dict(event),
            )
            return

        if stage == "index" and status == "written":
            _notify(
                request,
                stage="jsonl_index_written",
                message=(
                    f"Wrote {event.get('category')} index: "
                    f"{event.get('records', 0)} facts in {event.get('shards', 0)} shards"
                ),
                details=dict(event),
            )
            return

        messages = {
            ("compiler", "started"): "Compiling OpenAPI into indexed JSONL",
            ("compiler", "reused"): f"Reused JSONL cache: {request.output_path}",
            ("compiler", "completed"): f"JSONL cache ready: {request.output_path}",
            ("compiler", "failed"): "JSONL compilation failed",
        }
        message = messages.get((stage, status))
        if message:
            _notify(
                request,
                stage=f"jsonl_{status}",
                message=message,
                level="error" if status == "failed" else "info",
                details=dict(event),
            )

    result = compile_openapi_jsonl(
        request.input_path,
        request.output_path,
        reuse_unchanged=request.reuse_unchanged,
        progress=progress,
    )

    files = _cache_files(result.cache_dir, result.manifest.to_json())
    queue = result.queue_stats
    return JsonlOutput(
        input_path=request.input_path,
        output_path=result.cache_dir,
        reused=result.reused,
        records=result.records_written,
        definitions=result.definitions_written,
        mentions=result.mentions_written,
        dependencies=result.dependencies_written,
        files=files,
        record_queue_high_water=queue.record_high_water,
        pending_bytes_high_water=queue.pending_bytes_high_water,
        event_queue_high_water=queue.event_high_water,
        record_waits=queue.record_waits,
        event_waits=queue.event_waits,
    )


def _cache_files(cache_dir: Path, manifest: Mapping[str, Any]) -> list[Path]:
    relative_files: set[str] = {"manifest.json"}

    sections = manifest.get("sections", {})
    if isinstance(sections, Mapping):
        for raw in sections.values():
            if isinstance(raw, Mapping) and isinstance(raw.get("file"), str):
                relative_files.add(str(raw["file"]))

    events = manifest.get("events")
    if isinstance(events, Mapping) and isinstance(events.get("file"), str):
        relative_files.add(str(events["file"]))

    indexes = manifest.get("indexes", {})
    if isinstance(indexes, Mapping):
        for raw in indexes.values():
            if not isinstance(raw, Mapping):
                continue
            directory = raw.get("directory")
            shards = raw.get("shards")
            if not isinstance(directory, str) or not isinstance(shards, list):
                continue
            for shard in shards:
                if isinstance(shard, str):
                    relative_files.add(
                        PurePosixPath(directory, f"{shard}.jsonl").as_posix()
                    )

    return [cache_dir / Path(*PurePosixPath(item).parts) for item in sorted(relative_files)]


def _notify(
    request: JsonlInput,
    *,
    stage: str,
    message: str,
    level: str = "info",
    details: dict[str, Any] | None = None,
) -> None:
    if request.progress is None:
        return
    request.progress(
        RuntimeEvent(
            stage=stage,
            message=message,
            level=level,
            details=details or {},
        )
    )
