from __future__ import annotations

import argparse
from pathlib import Path

from dryv.ir import (
    Contract,
    Group,
    GuidanceKind,
    GuidanceNote,
    KernelData,
    Name,
    Schema,
    SchemaField,
    SchemaKind,
    SemanticId,
    TagSet,
    TypeExpression,
    contract_from_json,
    contract_from_yaml,
    contract_to_json,
    contract_to_yaml,
    validate_contract,
)

ROOT = Path(__file__).resolve().parent


def _field(
    identifier: str,
    name: str,
    primitive: str,
    *,
    required: bool = True,
    nullable: bool = False,
    readonly: bool = False,
) -> SchemaField:
    return SchemaField(
        id=SemanticId(identifier),
        name=Name(name),
        type=TypeExpression.primitive(primitive),
        required=required,
        nullable=nullable,
        readonly=readonly,
    )


def build_contract(*, include_ticket: bool = True) -> Contract:
    role = Schema(
        id=SemanticId("accounts.schema.role"),
        name=Name("Role"),
        kind=SchemaKind.ENUM,
        enum_values=("admin", "customer", "organiser"),
        data=KernelData(tags=TagSet(("domain:identity",))),
    )
    user = Schema(
        id=SemanticId("accounts.schema.user"),
        name=Name("User"),
        kind=SchemaKind.OBJECT,
        fields=(
            _field("accounts.schema.user.field.id", "id", "string", readonly=True),
            _field("accounts.schema.user.field.email", "email", "string"),
            _field("accounts.schema.user.field.active", "isActive", "boolean"),
            _field(
                "accounts.schema.user.field.age",
                "age",
                "integer",
                required=False,
                nullable=True,
            ),
        ),
        data=KernelData(
            tags=TagSet(("domain:audited", "ui:data-table")),
            guidance=(
                GuidanceNote(
                    GuidanceKind.EXPLAIN,
                    "A neutral account record used by the manual generation workspace.",
                ),
                GuidanceNote(
                    GuidanceKind.TESTING,
                    "Generated TypeScript and Dart outputs must compile without edits.",
                ),
            ),
        ),
    )
    schemas: tuple[Schema, ...] = (role, user)
    if include_ticket:
        ticket = Schema(
            id=SemanticId("accounts.schema.ticket"),
            name=Name("Ticket"),
            kind=SchemaKind.OBJECT,
            fields=(
                _field("accounts.schema.ticket.field.code", "code", "string"),
                _field(
                    "accounts.schema.ticket.field.price_cents",
                    "priceCents",
                    "integer",
                ),
                _field(
                    "accounts.schema.ticket.field.note",
                    "note",
                    "string",
                    required=False,
                    nullable=True,
                ),
            ),
            data=KernelData(tags=TagSet(("domain:audited",))),
        )
        schemas = (*schemas, ticket)

    return Contract(
        id=SemanticId("manual.connected.contract"),
        name=Name("Manual Connected Project"),
        version="1.0.0",
        groups=(
            Group(
                id=SemanticId("accounts.group"),
                name=Name("Accounts"),
                path=("accounts",),
                schemas=schemas,
                data=KernelData(
                    guidance=(
                        GuidanceNote(
                            GuidanceKind.IMPLEMENT,
                            "Generate the same semantic contract into two target-language packs.",
                        ),
                    )
                ),
            ),
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--without-ticket",
        action="store_true",
        help="Omit Ticket to manually test stale managed-file deletion.",
    )
    args = parser.parse_args()

    contract = build_contract(include_ticket=not args.without_ticket)
    diagnostics = validate_contract(contract)
    if diagnostics.has_errors:
        for diagnostic in diagnostics:
            print(f"{diagnostic.code}: {diagnostic.message}")
        return 1

    json_text = contract_to_json(contract)
    yaml_text = contract_to_yaml(contract)
    (ROOT / "contract.codepot.json").write_text(json_text, encoding="utf-8")
    (ROOT / "contract.codepot.yaml").write_text(yaml_text, encoding="utf-8")

    assert contract_from_json(json_text) == contract
    assert contract_from_yaml(yaml_text) == contract

    print(f"wrote {ROOT / 'contract.codepot.json'}")
    print(f"wrote {ROOT / 'contract.codepot.yaml'}")
    print(f"schemas: {sum(len(group.schemas) for group in contract.groups)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
