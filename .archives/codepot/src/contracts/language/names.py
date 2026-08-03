"""Language-safe naming contracts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageName:
    """Language-safe names prepared for one item.

    These names are derived from spec names plus language naming rules and
    reserved-keyword escaping.
    """

    class_name: str | None = None
    interface_name: str | None = None
    enum_name: str | None = None
    enum_value_name: str | None = None
    field_name: str | None = None
    method_name: str | None = None
    function_name: str | None = None
    constant_name: str | None = None
    variable_name: str | None = None
    file_name: str | None = None
    module_name: str | None = None
    package_name: str | None = None

    is_reserved: bool = False
    escaped: bool = False
    escape_reason: str | None = None
