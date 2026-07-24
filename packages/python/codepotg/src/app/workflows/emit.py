"""App emit workflow.

Orchestrates JSONL compilation, compatibility inference, language adaptation,
and either legacy or approved graph-based template emission.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path
from typing import Any

from app.models import EmitInput, EmitOutput, RuntimeDiagnostic, RuntimeEvent
from app.workflows.template_paths import resolve_template_root
from emission.bounded_graph_engine import emit_bounded_graph
from emission.engine import emit as run_legacy_emission
from emission.paths.config_loader import load_path_config
from inference.engine import InferenceEngine
from inference.lossless_contract import build_api_contract
from languages.discovery import resolve_language_adapter
from openapi.jsonl import compile_openapi_source_jsonl
from openapi.loader import load_openapi_document


def run_emit(request: EmitInput) -> EmitOutput:
    """Run the emit workflow and return structured output."""

    cache_path = _generation_cache_path(request.input_path)
    pre_diagnostics: list[RuntimeDiagnostic] = []
    seen_jsonl_files: set[str] = set()

    def jsonl_progress(event: Mapping[str, Any]) -> None:
        stage = str(event.get("stage", "jsonl"))
        status = str(event.get("status", "progress"))
        relative = event.get("file")
        if stage == "input" and status == "compatibility":
            warning = str(event.get("warning", "YAML compatibility conversion in use"))
            pre_diagnostics.append(RuntimeDiagnostic(level="warning", message=warning))
            _notify(
                request,
                stage="jsonl_compatibility_warning",
                message=warning,
                level="warning",
            )
            return
        if stage == "record" and status == "written" and isinstance(relative, str):
            if relative in seen_jsonl_files:
                return
            seen_jsonl_files.add(relative)
            _notify(
                request,
                stage="jsonl_file_writing",
                message=f"Writing JSONL: {cache_path / Path(relative)}",
            )
            return
        messages = {
            ("compiler", "started"): "Compiling OpenAPI into indexed JSONL",
            ("compiler", "reused"): f"Reused JSONL cache: {cache_path}",
            ("compiler", "completed"): f"JSONL cache ready: {cache_path}",
            ("compiler", "failed"): "JSONL compilation failed",
        }
        message = messages.get((stage, status))
        if message:
            _notify(
                request,
                stage=f"jsonl_{status}",
                message=message,
                level="error" if status == "failed" else "info",
            )

    jsonl_result = compile_openapi_source_jsonl(
        request.input_path,
        cache_path,
        progress=jsonl_progress,
    )
    pre_diagnostics.append(
        RuntimeDiagnostic(
            level="info",
            message=(
                f"JSONL cache {'reused' if jsonl_result.reused else 'compiled'}: "
                f"{jsonl_result.cache_dir}"
            ),
        )
    )

    _notify(
        request,
        stage="loading_openapi",
        message=f"Loading compatibility OpenAPI contract: {request.input_path}",
    )
    document = load_openapi_document(request.input_path)

    _notify(
        request,
        stage="inferring_schemas",
        message="Inferring schemas",
    )
    _notify(
        request,
        stage="inferring_operations",
        message="Inferring operations",
    )
    graph = InferenceEngine().infer(document)

    _notify(
        request,
        stage="building_contract",
        message="Building compatibility API contract",
    )
    api_contract = build_api_contract(graph)

    _notify(
        request,
        stage="resolving_language",
        message=f"Resolving language adapter: {request.language}",
    )
    adapter = resolve_language_adapter(request.language)
    template_root = resolve_template_root(
        adapter=adapter,
        templates_path=request.templates_path,
    )

    _notify(
        request,
        stage="planning_output_files",
        message="Planning output files",
    )
    template_contract = adapter.build_template_contract(
        api=api_contract,
        output_path=request.output_path,
        template_root=template_root,
        dry_run=request.dry_run,
        frontend=request.frontend,
        progress=request.progress,
    )
    template_contract = replace(
        template_contract,
        emit=replace(
            template_contract.emit,
            meta={
                **template_contract.emit.meta,
                "jsonl_cache": str(jsonl_result.cache_dir),
                "jsonl_reused": jsonl_result.reused,
            },
        ),
    )

    path_config = load_path_config(template_root)
    if path_config.uses_graph:
        _notify(
            request,
            stage="rendering_writing_files",
            message="Rendering dependency graph with bounded globals and queues",
        )
        emission_result = emit_bounded_graph(
            template_contract,
            progress=request.progress,
        )
    else:
        _notify(
            request,
            stage="rendering_writing_files",
            message="Rendering/writing files",
        )
        emission_result = run_legacy_emission(
            template_contract,
            progress=request.progress,
        )

    _notify(
        request,
        stage="language_post_actions",
        message="Running language post-actions",
    )
    post_result = adapter.after_emit(
        result=emission_result,
        progress=request.progress,
    )

    _notify(
        request,
        stage="emission_complete",
        message="Emission completed",
        total=len(emission_result.plan.files),
    )

    write_result = emission_result.write_result
    diagnostics = [
        *pre_diagnostics,
        RuntimeDiagnostic(
            level="info",
            message=(
                "Emission completed: "
                f"{len(write_result.created)} created, "
                f"{len(write_result.updated)} updated, "
                f"{len(write_result.unchanged)} unchanged, "
                f"{len(write_result.skipped)} skipped."
            ),
        ),
        RuntimeDiagnostic(
            level="info",
            message=(
                "Managed: "
                f"{len(write_result.created) - len(write_result.immutable_created)} created, "
                f"{len(write_result.updated)} updated, "
                f"{len(write_result.unchanged)} unchanged. "
                "Immutable: "
                f"{len(write_result.immutable_created)} created, "
                f"{len(write_result.immutable_skipped)} skipped existing. "
                f"Refused: {len(write_result.refused)}."
            ),
        ),
    ]
    queue_stats = emission_result.queue_stats
    if queue_stats is not None:
        diagnostics.append(
            RuntimeDiagnostic(
                level="info",
                message=(
                    "Graph queues: "
                    f"files peak={queue_stats.pending_files_high_water}, "
                    f"bytes peak={queue_stats.pending_bytes_high_water}, "
                    f"waits={queue_stats.queue_waits}, "
                    f"written={queue_stats.files_written}."
                ),
            )
        )

    diagnostics.extend(
        RuntimeDiagnostic(level="info", message=message)
        for message in post_result.diagnostics
    )

    return EmitOutput(
        input_path=request.input_path,
        language=request.language,
        output_path=request.output_path,
        dry_run=request.dry_run,
        planned=[file.output_path for file in emission_result.plan.files],
        written=list(write_result.created),
        updated=list(write_result.updated),
        unchanged=list(write_result.unchanged),
        skipped=list(write_result.skipped),
        immutable_created=list(write_result.immutable_created),
        immutable_skipped=list(write_result.immutable_skipped),
        refused=list(write_result.refused),
        diagnostics=diagnostics,
    )


def _generation_cache_path(input_path: Path) -> Path:
    source = input_path.expanduser().resolve()
    return source.parent / ".codepotg" / "cache" / source.stem


def _notify(
    request: EmitInput,
    *,
    stage: str,
    message: str,
    level: str = "info",
    current: int | None = None,
    total: int | None = None,
) -> None:
    """Emit a runtime progress event when a sink is provided."""

    if request.progress is None:
        return

    request.progress(
        RuntimeEvent(
            stage=stage,
            message=message,
            level=level,
            current=current,
            total=total,
        )
    )
