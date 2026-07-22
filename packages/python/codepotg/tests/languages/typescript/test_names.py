"""Tests for TypeScript naming helpers."""

from __future__ import annotations

from src.languages.typescript.names import safe_enum_key


def test_safe_enum_key_preserves_camel_case_values() -> None:
    assert safe_enum_key("companyId") == "companyId"
    assert safe_enum_key("weeklySchedule") == "weeklySchedule"
    assert safe_enum_key("isAvailableNow") == "isAvailableNow"
    assert safe_enum_key("createdAt") == "createdAt"
    assert safe_enum_key("updatedAt") == "updatedAt"


def test_safe_enum_key_preserves_camel_case_sort_values() -> None:
    assert safe_enum_key("-companyId") == "companyIdDesc"
    assert safe_enum_key("-weeklySchedule") == "weeklyScheduleDesc"
    assert safe_enum_key("+isAvailableNow") == "isAvailableNowAsc"


def test_safe_enum_key_still_normalizes_separated_values() -> None:
    assert safe_enum_key("company_owner") == "companyOwner"
    assert safe_enum_key("service-provider") == "serviceProvider"


def test_safe_enum_key_normalizes_all_caps_values() -> None:
    assert safe_enum_key("KES") == "kes"
    assert safe_enum_key("USD") == "usd"
    assert safe_enum_key("-USD") == "usdDesc"
