"""Tests for TypeScript schema template metadata."""

from __future__ import annotations

from pathlib import Path

from src.contracts.api import (
    ApiContract,
    ApiDocumentInfo,
    ApiField,
    ApiFieldKind,
    ApiFieldType,
    ApiSchema,
    ApiSchemaGroups,
    ApiSchemaKind,
)
from src.contracts.names import make_contract_name
from src.languages.typescript.adapter import TypeScriptLanguageAdapter


def test_typescript_override_schema_redefines_parent_fields_and_imports_parent_field_dependencies(
    tmp_path: Path,
) -> None:
    """Field overrides flatten parent fields but still import parent field types."""
    company_ref = "#/components/schemas/CompanyPublic"
    location_ref = "#/components/schemas/GeoLocation"
    partial_ref = "#/components/schemas/CompanyPartial"

    location = ApiSchema(
        id="GeoLocation",
        name=make_contract_name("GeoLocation"),
        ref=location_ref,
        kind=ApiSchemaKind.MODEL,
        resource="shared",
    )
    company = ApiSchema(
        id="CompanyPublic",
        name=make_contract_name("CompanyPublic"),
        ref=company_ref,
        kind=ApiSchemaKind.MODEL,
        resource="companies",
        dependencies=(location_ref,),
        fields=(
            ApiField(
                id="name",
                name=make_contract_name("name"),
                type=ApiFieldType(kind=ApiFieldKind.PRIMITIVE, type="string"),
            ),
            ApiField(
                id="location",
                name=make_contract_name("location"),
                type=ApiFieldType(kind=ApiFieldKind.MODEL, type="GeoLocation"),
                schema_ref=location_ref,
                schema_refs=(location_ref,),
            ),
        ),
    )
    partial = ApiSchema(
        id="CompanyPartial",
        name=make_contract_name("CompanyPartial"),
        ref=partial_ref,
        kind=ApiSchemaKind.MODEL,
        resource="companies",
        inherited_refs=(company_ref,),
        has_field_overrides=True,
        fields=(
            ApiField(
                id="name",
                name=make_contract_name("name"),
                required=False,
                type=ApiFieldType(kind=ApiFieldKind.PRIMITIVE, type="string"),
            ),
        ),
    )

    api = ApiContract(
        info=ApiDocumentInfo(title="Override API", api_version="v1"),
        schemas=ApiSchemaGroups(
            all=(location, company, partial),
            models=(location, company, partial),
        ),
    )

    contract = TypeScriptLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    schema = contract.schemas.all[2]

    assert schema.meta.has_extends is False
    assert schema.meta.extends_type is None
    assert tuple(field.lang.display_name for field in schema.fields) == (
        "name",
        "location",
    )
    assert schema.fields[0].api.required is False

    imports = tuple(item.ref for item in schema.emit.imports)

    assert company_ref not in imports
    assert location_ref in imports


def test_typescript_field_keys_keep_contract_names_even_when_reserved(
    tmp_path: Path,
) -> None:
    """Object property keys do not need symbol-safe reserved-word rewriting."""
    schema_ref = "#/components/schemas/EventPayload"
    schema = ApiSchema(
        id="EventPayload",
        name=make_contract_name("EventPayload"),
        ref=schema_ref,
        kind=ApiSchemaKind.DTO,
        fields=(
            ApiField(
                id="type",
                name=make_contract_name("type"),
                type=ApiFieldType(kind=ApiFieldKind.PRIMITIVE, type="string"),
            ),
            ApiField(
                id="default",
                name=make_contract_name("default"),
                type=ApiFieldType(kind=ApiFieldKind.PRIMITIVE, type="boolean"),
            ),
        ),
    )
    api = ApiContract(
        info=ApiDocumentInfo(title="Reserved Keys API", api_version="v1"),
        schemas=ApiSchemaGroups(all=(schema,), dtos=(schema,)),
    )

    contract = TypeScriptLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    fields = contract.schemas.all[0].fields

    assert tuple(field.lang.display_name for field in fields) == ("type", "default")
