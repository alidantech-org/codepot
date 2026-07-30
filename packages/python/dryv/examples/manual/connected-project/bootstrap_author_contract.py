from __future__ import annotations

import argparse
from pathlib import Path

from dryv.ir import (
    contract_from_json,
    contract_from_yaml,
    contract_to_json,
    contract_to_yaml,
)
from dryv_author import Author, field

ROOT = Path(__file__).resolve().parent


def build_author(*, include_ticket: bool = True) -> Author:
    author = Author("Manual Author Connected Project", version="1.0.0")
    accounts = author.group("Accounts", declaration_id="accounts.group")

    author.enum_schema(
        "Role",
        ("admin", "customer", "organiser"),
        declaration_id="accounts.schema.role",
        group=accounts,
    )
    author.schema(
        "User",
        {
            "id": field(str, readonly=True),
            "email": field(str),
            "isActive": field(bool),
            "age": field(int, required=False, nullable=True),
        },
        declaration_id="accounts.schema.user",
        group=accounts,
    )
    if include_ticket:
        author.schema(
            "Ticket",
            {
                "code": field(str),
                "priceCents": field(int),
                "note": field(str, required=False, nullable=True),
            },
            declaration_id="accounts.schema.ticket",
            group=accounts,
        )
    return author


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--without-ticket",
        action="store_true",
        help="Omit Ticket to test stale managed-file deletion for the authoring route.",
    )
    args = parser.parse_args()

    result = build_author(include_ticket=not args.without_ticket).compile()
    for diagnostic in result.diagnostics:
        print(f"{diagnostic.code}: {diagnostic.message}")
    if not result.ok or result.contract is None:
        return 1

    # The orchestrator bridge deliberately uses the core-owned canonical codec.
    json_text = contract_to_json(result.contract)
    yaml_text = contract_to_yaml(result.contract)
    (ROOT / "contract.author.codepot.json").write_text(json_text, encoding="utf-8")
    (ROOT / "contract.author.codepot.yaml").write_text(yaml_text, encoding="utf-8")

    assert contract_from_json(json_text) == result.contract
    assert contract_from_yaml(yaml_text) == result.contract

    print(f"contract: {result.contract.id}")
    print(f"groups: {len(result.contract.groups)}")
    print(f"schemas: {sum(len(group.schemas) for group in result.contract.groups)}")
    print(f"wrote {ROOT / 'contract.author.codepot.json'}")
    print(f"wrote {ROOT / 'contract.author.codepot.yaml'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
