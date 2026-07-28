"""Production type-system coverage for the five additional adapters."""

from __future__ import annotations

import pytest

from languages.portable_types import TYPE_SYSTEMS, type_system_for


@pytest.mark.parametrize(
    ("language", "scalar", "format_name", "expected_scalar", "expected_format"),
    (
        ("python", "string", "date-time", "str", "datetime.datetime"),
        ("java", "integer", "uuid", "Long", "UUID"),
        ("csharp", "boolean", "date", "bool", "DateOnly"),
        ("go", "number", "binary", "float64", "[]byte"),
        ("rust", "object", "decimal", "serde_json::Value", "rust_decimal::Decimal"),
    ),
)
def test_type_system_resolves_scalars_and_formats(
    language: str,
    scalar: str,
    format_name: str,
    expected_scalar: str,
    expected_format: str,
) -> None:
    system = type_system_for(language)

    assert system.resolve(scalar) == expected_scalar
    assert system.resolve("string", format=format_name) == expected_format
    assert system.file_extension.startswith(".")
    assert system.package_file
    assert system.source_root


@pytest.mark.parametrize(
    ("language", "expected_array", "expected_map", "expected_nullable"),
    (
        ("python", "list[str]", "dict[str, int]", "str | None"),
        ("java", "List<String>", "Map<String, Long>", "String"),
        ("csharp", "List<string>", "Dictionary<string, long>", "string?"),
        ("go", "[]string", "map[string]int64", "*string"),
        ("rust", "Vec<String>", "std::collections::BTreeMap<String, i64>", "Option<String>"),
    ),
)
def test_type_system_resolves_collections_and_nullability(
    language: str,
    expected_array: str,
    expected_map: str,
    expected_nullable: str,
) -> None:
    system = type_system_for(language)
    string_type = system.resolve("string")
    integer_type = system.resolve("integer")

    assert system.resolve("array", item_type=string_type) == expected_array
    assert system.resolve("object", value_type=integer_type) == expected_map
    assert system.resolve("string", nullable=True) == expected_nullable


def test_all_registered_type_systems_have_unique_target_conventions() -> None:
    assert set(TYPE_SYSTEMS) == {"python", "java", "csharp", "go", "rust"}
    assert len({system.file_extension for system in TYPE_SYSTEMS.values()}) == 5
    assert len({system.package_file for system in TYPE_SYSTEMS.values()}) == 5


def test_unknown_type_uses_target_fallback() -> None:
    assert type_system_for("python").resolve("future-type") == "object"
    assert type_system_for("go").resolve("future-type") == "any"
    assert type_system_for("rust").resolve("future-type") == "serde_json::Value"


def test_unknown_language_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported portable target language"):
        type_system_for("kotlin")
