from __future__ import annotations

from typing import Any

from dryv.api import OperationResult
from dryv.generation import GenerationData
from dryv.ports import ManagedWriteReport
from dryv.runtime import RuntimeSnapshot


def result_document(
    result: OperationResult[GenerationData],
    *,
    report: ManagedWriteReport | None = None,
) -> dict[str, Any]:
    data = result.data
    plan = data.plan if data is not None else None
    output = data.output if data is not None else None

    document: dict[str, Any] = {
        "operationId": result.operation_id,
        "status": result.status.value,
        "diagnostics": result.diagnostics.to_dict(),
        "artifacts": tuple(
            {
                "id": artifact.id,
                "kind": artifact.kind.value,
                "pack": artifact.pack_instance,
                "path": artifact.output_path,
                "selection": artifact.selection_key,
                "semanticId": artifact.semantic_id,
                "target": artifact.target_id,
                "template": artifact.template_id,
            }
            for artifact in (plan.artifacts if plan is not None else ())
        ),
    }
    if output is not None:
        document["generated"] = tuple(
            {
                "bytes": len(artifact.content),
                "id": artifact.id,
                "path": artifact.path,
                "semanticId": artifact.semantic_id,
                "target": artifact.target_id,
                "template": artifact.template_id,
            }
            for artifact in output.artifacts
        )
    if report is not None:
        document["writes"] = tuple(
            {"kind": change.kind.value, "path": change.path} for change in report.changes
        )
    return document


def runtime_document(snapshot: RuntimeSnapshot) -> dict[str, Any]:
    return {
        "coreVersion": snapshot.core_version,
        "plugins": tuple(
            {
                "aliases": plugin.aliases,
                "capabilities": plugin.capabilities,
                "category": plugin.category.value,
                "distribution": plugin.distribution,
                "id": plugin.id,
                "provides": plugin.provides,
                "version": plugin.version,
            }
            for plugin in snapshot.plugins
        ),
    }
