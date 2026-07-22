"""Tests for Dart-safe naming helpers."""

from __future__ import annotations

from src.languages.dart.names import safe_dart_identifier, safe_enum_key


def test_safe_enum_key_preserves_camel_case_values() -> None:
    assert safe_enum_key("isOnline") == "isOnline"
    assert safe_enum_key("emailVerified") == "emailVerified"
    assert safe_enum_key("createdAt") == "createdAt"
    assert safe_enum_key("updatedAt") == "updatedAt"


def test_safe_enum_key_preserves_camel_case_sort_values() -> None:
    assert safe_enum_key("-isOnline") == "isOnlineDesc"
    assert safe_enum_key("-emailVerified") == "emailVerifiedDesc"
    assert safe_enum_key("-createdAt") == "createdAtDesc"
    assert safe_enum_key("+updatedAt") == "updatedAtAsc"


def test_safe_enum_key_still_normalizes_separated_values() -> None:
    assert safe_enum_key("email_verified") == "emailVerified"
    assert safe_enum_key("created-at") == "createdAt"


def test_safe_dart_identifier_allows_type_as_field_name() -> None:
    assert safe_dart_identifier("type") == "type"
