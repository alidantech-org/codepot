"""Tests for field query metadata extraction."""

from __future__ import annotations

from src.inference.schemas.fields import infer_schema_fields


def test_field_query_metadata_from_direct_x_codegen() -> None:
    """Test that field with direct x-codegen.query gets query metadata."""
    schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "x-codegen": {"query": {"filter": True, "operators": ["eq"]}},
            }
        },
    }

    fields = infer_schema_fields(schema, document=None)
    assert len(fields) == 1

    field = fields[0]
    assert field.name == "name"
    assert field.query is not None
    assert field.query.filterable is True
    assert field.query.operators == ("eq",)


def test_field_query_metadata_without_x_codegen() -> None:
    """Test that field without x-codegen.query gets empty query metadata."""
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
        },
    }

    fields = infer_schema_fields(schema, document=None)
    assert len(fields) == 1

    field = fields[0]
    assert field.name == "name"
    assert field.query is not None
    assert field.query.filterable is False
    assert field.query.operators == ()
    assert field.query.sortable is False
    assert field.query.selectable is False
    assert field.query.searchable is False


def test_field_query_metadata_with_all_options() -> None:
    """Test that field with all query options gets complete metadata."""
    schema = {
        "type": "object",
        "properties": {
            "age": {
                "type": "integer",
                "x-codegen": {
                    "query": {
                        "filter": True,
                        "operators": ["eq", "gt", "lt"],
                        "sort": True,
                        "select": True,
                    }
                },
            }
        },
    }

    fields = infer_schema_fields(schema, document=None)
    assert len(fields) == 1

    field = fields[0]
    assert field.name == "age"
    assert field.query is not None
    assert field.query.filterable is True
    assert field.query.operators == ("eq", "gt", "lt")
    assert field.query.sortable is True
    assert field.query.selectable is True
