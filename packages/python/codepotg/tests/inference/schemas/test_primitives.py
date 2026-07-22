"""Tests for query metadata inference."""

from __future__ import annotations

from src.inference.metadata.query import infer_query_metadata


def test_infer_query_metadata_from_empty_schema() -> None:
    """Test that empty schema returns empty QueryMetadata."""
    result = infer_query_metadata(None)
    assert result.filterable is False
    assert result.operators == ()
    assert result.sortable is False
    assert result.selectable is False
    assert result.searchable is False


def test_infer_query_metadata_from_empty_dict() -> None:
    """Test that empty dict returns empty QueryMetadata."""
    result = infer_query_metadata({})
    assert result.filterable is False
    assert result.operators == ()
    assert result.sortable is False
    assert result.selectable is False
    assert result.searchable is False


def test_infer_query_metadata_without_x_codegen() -> None:
    """Test that schema without x-codegen returns empty QueryMetadata."""
    result = infer_query_metadata({"type": "string"})
    assert result.filterable is False
    assert result.operators == ()


def test_infer_query_metadata_without_query_key() -> None:
    """Test that x-codegen without query key returns empty QueryMetadata."""
    result = infer_query_metadata({"x-codegen": {"kind": "primitive"}})
    assert result.filterable is False
    assert result.operators == ()


def test_infer_query_metadata_with_filter() -> None:
    """Test extracting filter option."""
    result = infer_query_metadata({"x-codegen": {"query": {"filter": True}}})
    assert result.filterable is True
    assert result.operators == ()
    assert result.sortable is False


def test_infer_query_metadata_with_operators_list() -> None:
    """Test extracting operators as list."""
    result = infer_query_metadata({"x-codegen": {"query": {"operators": ["eq", "in", "gt"]}}})
    assert result.operators == ("eq", "in", "gt")


def test_infer_query_metadata_with_operators_string() -> None:
    """Test extracting operators as string."""
    result = infer_query_metadata({"x-codegen": {"query": {"operators": "eq"}}})
    assert result.operators == ("eq",)


def test_infer_query_metadata_with_sort() -> None:
    """Test extracting sort option."""
    result = infer_query_metadata({"x-codegen": {"query": {"sort": True}}})
    assert result.sortable is True


def test_infer_query_metadata_with_select() -> None:
    """Test extracting select option."""
    result = infer_query_metadata({"x-codegen": {"query": {"select": True}}})
    assert result.selectable is True


def test_infer_query_metadata_with_all_options() -> None:
    """Test extracting all query options."""
    result = infer_query_metadata(
        {
            "x-codegen": {
                "query": {
                    "filter": True,
                    "operators": ["eq", "in", "gt", "lt"],
                    "sort": True,
                    "select": True,
                }
            }
        }
    )
    assert result.filterable is True
    assert result.operators == ("eq", "in", "gt", "lt")
    assert result.sortable is True
    assert result.selectable is True
