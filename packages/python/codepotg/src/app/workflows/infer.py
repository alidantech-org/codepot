"""Runtime inference workflow."""

from __future__ import annotations

from collections import Counter

from inference.engine import InferenceEngine
from openapi.loader import load_openapi_document
from app.io.inference_output import write_inference_graph
from app.models import (
    AliasSchemaSummary,
    InferInput,
    InferOutput,
    RuntimeDiagnostic,
    RuntimeEvent,
    UnknownSchemaSummary,
)


def run_infer(request: InferInput) -> InferOutput:
    """Run inference and return structured output."""
    _notify(request, stage="loading_openapi", message="Loading OpenAPI document")
    document = load_openapi_document(request.input_path)

    _notify(request, stage="running_inference", message="Running inference engine")
    graph = InferenceEngine().infer(document)

    written = []
    if request.output_path is not None:
        _notify(
            request,
            stage="writing_inference_output",
            message=f"Writing inference graph to {request.output_path}",
        )
        written.append(write_inference_graph(graph, request.output_path))

    schemas = list(getattr(graph, "schemas", []) or [])
    alias_schemas = [schema for schema in schemas if bool(getattr(schema, "is_alias", False))]
    unknown_schemas = [schema for schema in schemas if getattr(getattr(schema, "kind", None), "value", "") == "unknown"]
    kind_counts = Counter(str(getattr(getattr(schema, "kind", None), "value", "-")) for schema in schemas)

    _notify(request, stage="inference_complete", message="Inference completed")

    return InferOutput(
        input_path=request.input_path,
        output_path=request.output_path,
        graph=graph,
        title=str(getattr(graph, "title", "-")),
        openapi_version=str(getattr(graph, "openapi_version", "-")),
        api_version=str(getattr(graph, "api_version", "-")),
        resources_count=len(list(getattr(graph, "resources", []) or [])),
        schemas_count=len(schemas),
        operations_count=len(list(getattr(graph, "operations", []) or [])),
        dependencies_count=len(list(getattr(graph, "dependencies", []) or [])),
        alias_schemas_count=len(alias_schemas),
        schema_kind_counts=dict(sorted(kind_counts.items())),
        unknown_schemas=[
            UnknownSchemaSummary(
                name=str(getattr(schema, "name", "-")),
                ref=str(getattr(schema, "ref", "-")),
                x_codegen_kind=str(
                    getattr(schema, "x_codegen", {}).get("kind", "-") if isinstance(getattr(schema, "x_codegen", {}), dict) else "-"
                ),
                keys=sorted(list(getattr(schema, "raw", {}).keys())) if isinstance(getattr(schema, "raw", {}), dict) else [],
            )
            for schema in unknown_schemas
        ],
        alias_schemas=[
            AliasSchemaSummary(
                name=str(getattr(schema, "name", "-")),
                kind=str(getattr(getattr(schema, "kind", None), "value", "-")),
                alias_of=str(getattr(schema, "alias_of", None) or "-"),
                resource=str(getattr(getattr(schema, "resource", None), "name", "-")),
            )
            for schema in alias_schemas
        ],
        written=written,
        diagnostics=[RuntimeDiagnostic(level="info", message="Inference completed.")],
    )


def _notify(
    request: InferInput,
    *,
    stage: str,
    message: str,
    level: str = "info",
    current: int | None = None,
    total: int | None = None,
) -> None:
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
