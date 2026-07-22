"""Python naming helpers."""

from __future__ import annotations

from archives.codepot.src.contracts.language.names import LanguageName
from archives.codepot.src.contracts.spec.names import SpecName, SpecNameCase, resolve_name_case
from archives.codepot.src.languages.python.constants import RESERVED_WORD_ESCAPE_REASON, RESERVED_WORD_SUFFIX
from archives.codepot.src.languages.python.keywords import is_python_reserved


def _escape(value: str) -> tuple[str, bool, str | None]:
    """Escape a Python name if needed."""

    if is_python_reserved(value):
        return f"{value}{RESERVED_WORD_SUFFIX}", True, RESERVED_WORD_ESCAPE_REASON

    return value, False, None


def make_python_name(
    name: SpecName,
    *,
    class_case: SpecNameCase = SpecNameCase.PASCAL,
    interface_case: SpecNameCase = SpecNameCase.PASCAL,
    enum_case: SpecNameCase = SpecNameCase.PASCAL,
    enum_value_case: SpecNameCase = SpecNameCase.CONSTANT,
    field_case: SpecNameCase = SpecNameCase.SNAKE,
    method_case: SpecNameCase = SpecNameCase.SNAKE,
    function_case: SpecNameCase = SpecNameCase.SNAKE,
    constant_case: SpecNameCase = SpecNameCase.SCREAMING_SNAKE,
    file_case: SpecNameCase = SpecNameCase.SNAKE,
    module_case: SpecNameCase = SpecNameCase.SNAKE,
    package_case: SpecNameCase = SpecNameCase.SNAKE,
) -> LanguageName:
    """Create Python-safe language names."""

    class_name, class_escaped, class_reason = _escape(
        resolve_name_case(name, class_case)
    )
    field_name, field_escaped, field_reason = _escape(
        resolve_name_case(name, field_case)
    )
    method_name, method_escaped, method_reason = _escape(
        resolve_name_case(name, method_case)
    )

    escaped = class_escaped or field_escaped or method_escaped
    reason = class_reason or field_reason or method_reason

    return LanguageName(
        class_name=class_name,
        interface_name=resolve_name_case(name, interface_case),
        enum_name=resolve_name_case(name, enum_case),
        enum_value_name=resolve_name_case(name, enum_value_case),
        field_name=field_name,
        method_name=method_name,
        function_name=resolve_name_case(name, function_case),
        constant_name=resolve_name_case(name, constant_case),
        variable_name=field_name,
        file_name=resolve_name_case(name, file_case),
        module_name=resolve_name_case(name, module_case),
        package_name=resolve_name_case(name, package_case),
        is_reserved=escaped,
        escaped=escaped,
        escape_reason=reason,
    )
