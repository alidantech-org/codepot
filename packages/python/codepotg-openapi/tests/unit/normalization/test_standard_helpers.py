from __future__ import annotations

from codepotg_openapi.normalization.operation_responses import is_success, status_sort_key
from codepotg_openapi.normalization.schema_support import field_constraints, schema_types, title


def test_field_constraints_preserve_supported_facts() -> None:
    constraints = field_constraints(
        {
            "minimum": 1,
            "maximum": 10,
            "minLength": 2,
            "maxLength": 20,
            "pattern": "^[a-z]+$",
            "format": "slug",
        }
    )
    assert constraints.minimum == 1
    assert constraints.maximum == 10
    assert constraints.min_length == 2
    assert constraints.max_length == 20
    assert constraints.pattern == "^[a-z]+$"
    assert constraints.format == "slug"


def test_schema_type_and_name_helpers_are_deterministic() -> None:
    assert schema_types(["string", "null"]) == (True, ("string",))
    assert schema_types("integer") == (False, ("integer",))
    assert title("order-item") == "OrderItem"


def test_response_classification_is_deterministic() -> None:
    assert is_success("200") is True
    assert is_success("2XX") is True
    assert is_success("default") is False
    assert sorted(("default", "404", "200"), key=status_sort_key) == ["200", "404", "default"]
