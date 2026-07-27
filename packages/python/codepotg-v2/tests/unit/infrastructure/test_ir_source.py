from codepotg.api import CancellationToken
from codepotg.infrastructure.ir_source import create_plugin
from codepotg.ir import Contract, Group, Name, SemanticId, contract_to_json
from codepotg.ports import SourceAdapterRequest


def test_canonical_ir_source_adapter_round_trips_memory_documents() -> None:
    contract = Contract(
        id=SemanticId("example.contract"),
        name=Name("Example"),
        groups=(
            Group(
                id=SemanticId("example.group"),
                name=Name("Example"),
            ),
        ),
    )
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
