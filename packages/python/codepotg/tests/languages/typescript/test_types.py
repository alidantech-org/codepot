"""Tests for TypeScript type mapping."""

from __future__ import annotations

from src.contracts.api import ApiField, ApiFieldKind, ApiFieldType
from src.contracts.names import make_contract_name
from src.languages.typescript.types import ts_field_type


def test_date_time_string_fields_emit_date() -> None:
    field = ApiField(
        id="createdAt",
        name=make_contract_name("createdAt"),
        type=ApiFieldType(
            kind=ApiFieldKind.PRIMITIVE,
            type="string",
            format="date-time",
        ),
    )

    assert ts_field_type(field, {}) == "Date"


def test_date_string_fields_stay_string() -> None:
    field = ApiField(
        id="birthDate",
        name=make_contract_name("birthDate"),
        type=ApiFieldType(
            kind=ApiFieldKind.PRIMITIVE,
            type="string",
            format="date",
        ),
    )

    assert ts_field_type(field, {}) == "string"


def test_date_time_array_items_emit_date_array() -> None:
    field = ApiField(
        id="timestamps",
        name=make_contract_name("timestamps"),
        type=ApiFieldType(
            kind=ApiFieldKind.ARRAY,
            item_kind=ApiFieldKind.PRIMITIVE,
            item_type="string",
            item_format="date-time",
        ),
    )

    assert ts_field_type(field, {}) == "Array<Date>"
