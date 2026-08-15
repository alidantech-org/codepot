from pathlib import Path

from dryv.api import CancellationToken
from dryv.features.serialization import contract_to_json, contract_to_jsonl
from dryv.infrastructure.ir_source import create_plugin
from dryv.ir import Contract, Group, Name, SemanticId
from dryv.ports import SourceAdapterRequest


def _contract() -> Contract:
    return Contract(
        id=SemanticId("example.contract"),
        name=Name("Example"),
        groups=(
            Group(
                id=SemanticId("example.group"),
                name=Name("Example"),
            ),
        ),
    )


def test_canonical_ir_source_adapter_round_trips_memory_documents() -> None:
    contract = _contract()
    result = create_plugin().normalize(
        SourceAdapterRequest(
            source_id="contract",
            content=contract_to_json(contract),
        ),
        CancellationToken(),
    )

    assert not result.diagnostics.has_errors
    assert result.contract == contract
    assert result.digest is not None


def test_canonical_ir_source_adapter_routes_jsonl_through_serialization(
    tmp_path: Path,
) -> None:
    contract = _contract()
    source = tmp_path / "contract.jsonl"
    source.write_bytes(b"".join(contract_to_jsonl(contract)))

    result = create_plugin().normalize(
        SourceAdapterRequest(
            source_id="contract",
            location=str(source.resolve()),
        ),
        CancellationToken(),
    )

    assert not result.diagnostics.has_errors
    assert result.contract == contract
    assert result.digest is not None
