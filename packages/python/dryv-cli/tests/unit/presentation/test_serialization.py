from __future__ import annotations

from dryv.api import OperationResult, OperationStatus
from dryv.generation import GenerationData, GenerationPlan
from dryv.plugins import PluginCategory
from dryv.runtime import RuntimePluginInfo, RuntimeSnapshot

from dryv_cli.presentation.serialization import result_document, runtime_document


def test_result_document_is_stable_for_an_empty_ready_plan() -> None:
    result = OperationResult(
        status=OperationStatus.READY,
        data=GenerationData(
            plan=GenerationPlan(project_name="example", artifacts=()),
        ),
        operation_id="operation-1",
    )

    document = result_document(result)

    assert document == {
        "operationId": "operation-1",
        "status": "ready",
        "diagnostics": (),
        "artifacts": (),
    }


def test_runtime_document_preserves_public_plugin_inventory() -> None:
    snapshot = RuntimeSnapshot(
        core_version="2.0.0a1",
        plugins=(
            RuntimePluginInfo(
                id="ir",
                category=PluginCategory.SOURCE_ADAPTER,
                distribution="dryv",
                version="2.0.0a1",
                aliases=("codepot-ir",),
                capabilities=("source.ir",),
            ),
        ),
    )

    document = runtime_document(snapshot)

    assert document["coreVersion"] == "2.0.0a1"
    assert document["plugins"] == (
        {
            "aliases": ("codepot-ir",),
            "capabilities": ("source.ir",),
            "category": "source_adapter",
            "distribution": "dryv",
            "id": "ir",
            "provides": (),
            "version": "2.0.0a1",
        },
    )
