from __future__ import annotations

from pathlib import Path

from dryv.api import CancellationToken
from dryv.ir import (
    Contract,
    contract_from_json,
    contract_to_json,
    contract_to_yaml,
)
from dryv.ports import SourceAdapterRequest
from dryv_openapi import OpenApiSourceAdapter

ROOT = Path(__file__).resolve().parent


def _summary(label: str, contract: Contract) -> None:
    groups = contract.groups
    schemas = tuple(schema for group in groups for schema in group.schemas)
    operations = tuple(operation for group in groups for operation in group.operations)
    print(label)
    print(f"  id: {contract.id}")
    print(f"  name: {contract.name.value}")
    print(f"  groups: {tuple(group.name.value for group in groups)}")
    print(f"  schemas: {tuple(sorted(schema.name.value for schema in schemas))}")
    print(f"  operations: {tuple(sorted(operation.name.value for operation in operations))}")


def main() -> int:
    direct_path = ROOT / "contract.codepot.json"
    author_path = ROOT / "contract.author.codepot.json"
    missing = tuple(path.name for path in (direct_path, author_path) if not path.is_file())
    if missing:
        raise SystemExit(
            f"missing bootstrap outputs {missing}; run bootstrap_contract.py and "
            "bootstrap_author_contract.py first"
        )

    direct = contract_from_json(direct_path.read_text(encoding="utf-8"))
    author = contract_from_json(author_path.read_text(encoding="utf-8"))

    openapi_result = OpenApiSourceAdapter().normalize(
        SourceAdapterRequest(
            source_id="manual-openapi",
            location=str((ROOT / "openapi.yaml").resolve()),
        ),
        CancellationToken(),
    )
    for diagnostic in openapi_result.diagnostics:
        print(
            f"openapi diagnostic: {diagnostic.severity.name.lower()} "
            f"{diagnostic.code}: {diagnostic.message}"
        )
    if openapi_result.contract is None:
        return 1

    openapi = openapi_result.contract
    (ROOT / "contract.openapi.codepot.json").write_text(
        contract_to_json(openapi),
        encoding="utf-8",
    )
    (ROOT / "contract.openapi.codepot.yaml").write_text(
        contract_to_yaml(openapi),
        encoding="utf-8",
    )

    _summary("direct public IR", direct)
    _summary("dryv-author", author)
    _summary("standard OpenAPI", openapi)

    expected = {"Role", "Ticket", "User"}
    for label, contract in (
        ("direct", direct),
        ("author", author),
        ("openapi", openapi),
    ):
        names = {
            schema.name.value
            for group in contract.groups
            for schema in group.schemas
        }
        missing_names = tuple(sorted(expected - names))
        if missing_names:
            raise SystemExit(f"{label} source is missing expected schemas: {missing_names}")

    print(f"openapi digest: {openapi_result.digest}")
    print("all three sources produced generation-ready public contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
