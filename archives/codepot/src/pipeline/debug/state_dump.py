"""Pass-by-pass pipeline state snapshot writer."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from archives.codepot.src.pipeline.contracts.results import PassReport
from archives.codepot.src.pipeline.contracts.state import PipelineState
from archives.codepot.src.pipeline.debug.serializer import to_debug_json

DEBUG_ROOT = ".codepotx"
PASSES_DIR = "passes"


@dataclass(frozen=True)
class PipelineStateDumpRequest:
    """Request to dump one pass state snapshot."""

    index: int
    state: PipelineState
    report: PassReport


def _snapshot_path(
    *,
    output_root: Path,
    index: int,
    pass_name: str,
) -> Path:
    """Create output path for one pass snapshot."""

    filename = f"{index:02d}_{pass_name}.json"
    return output_root / DEBUG_ROOT / PASSES_DIR / filename


def _snapshot_payload(request: PipelineStateDumpRequest) -> dict[str, object]:
    """Build JSON payload for one pass snapshot."""

    return {
        "index": request.index,
        "pass": {
            "name": request.report.name,
            "title": request.report.title,
            "status": request.report.status,
            "message": request.report.message,
            "started_at": request.report.started_at,
            "finished_at": request.report.finished_at,
            "duration_ms": request.report.duration_ms,
            "counters": request.report.counters,
            "diagnostics": request.report.diagnostics,
            "debug": request.report.debug,
        },
        # "state": request.state,
    }


def write_pipeline_state_dump(request: PipelineStateDumpRequest) -> Path:
    """Write one pass state snapshot JSON file."""

    output_root = request.state.options.output_path
    path = _snapshot_path(
        output_root=output_root,
        index=request.index,
        pass_name=request.report.name,
    )

    path.parent.mkdir(parents=True, exist_ok=True)

    payload = to_debug_json(_snapshot_payload(request))
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    return path
