"""App emit workflow.

Orchestrates the full emission pipeline: OpenAPI loading, inference, contract
building, language adaptation, and template emission.
"""

from __future__ import annotations

from app.models import EmitInput, EmitOutput, RuntimeDiagnostic, RuntimeEvent
from app.workflows.template_paths import resolve_template_root
from emission.engine import emit as run_emission
from inference.engine import InferenceEngine
from inference.lossless_contract import build_api_contract
from languages.discovery import resolve_language_adapter
from openapi.loader import load_openapi_document


def run_emit(request: EmitInput) -> EmitOutput:
    """Run the emit workflow and return structured output."""
    _notify(
        request,
        stage="loading_openapi",
        message=f"Loading OpenAPI document: {request.input_path}",
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
        message="Building API contract",
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

    _notify(
        request,
        stage="rendering_writing_files",
        message="Rendering/writing files",
    )
    emission_result = run_emission(
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
        )
    ]

    diagnostics.extend(RuntimeDiagnostic(level="info", message=message) for message in post_result.diagnostics)  # noqa: E501

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
