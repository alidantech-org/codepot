"""Dart naming helpers."""

from __future__ import annotations

from archives.codepot.src.contracts.language.names import LanguageName
from archives.codepot.src.contracts.spec.names import SpecName
from archives.codepot.src.languages.dart.constants import RESERVED_WORD_ESCAPE_REASON, RESERVED_WORD_SUFFIX
from archives.codepot.src.languages.dart.keywords import is_dart_reserved


def _escape(value: str) -> tuple[str, bool, str | None]:
    """Escape a Dart name if needed."""

    if is_dart_reserved(value):
        return f"{value}{RESERVED_WORD_SUFFIX}", True, RESERVED_WORD_ESCAPE_REASON

    return value, False, None


def make_dart_name(
    name: SpecName,
    *,
    class_name: str,
    interface_name: str,
    enum_name: str,
    enum_value_name: str,
    field_name: str,
    method_name: str,
    function_name: str,
    constant_name: str,
    file_name: str,
    module_name: str,
    package_name: str,
) -> LanguageName:
    """Create Dart-safe language names from prepared typed values."""

    class_value, class_escaped, class_reason = _escape(class_name)
    field_value, field_escaped, field_reason = _escape(field_name)
    method_value, method_escaped, method_reason = _escape(method_name)

    escaped = class_escaped or field_escaped or method_escaped
    reason = class_reason or field_reason or method_reason

    return LanguageName(
        class_name=class_value,
        interface_name=interface_name,
        enum_name=enum_name,
        enum_value_name=enum_value_name,
        field_name=field_value,
        method_name=method_value,
        function_name=function_name,
        constant_name=constant_name,
        variable_name=field_value,
        file_name=file_name,
        module_name=module_name,
        package_name=package_name,
        is_reserved=escaped,
        escaped=escaped,
        escape_reason=reason,
    )
