from __future__ import annotations

from dryv.diagnostics import SourceKind
from dryv_template_jinja.diagnostics import error_diagnostic, undefined_name


def test_error_diagnostic_uses_template_source_and_sorted_details() -> None:
    diagnostic = error_diagnostic(
        "JINJA_SYNTAX",
        "invalid",
        template_id="root.jinja",
        line=2,
        details={"z": 1, "a": 2},
    )
    assert diagnostic.span is not None
    assert diagnostic.span.source.kind is SourceKind.TEMPLATE
    assert diagnostic.span.source.value == "root.jinja"
    assert diagnostic.span.start.line == 2
    assert diagnostic.details == (("a", 2), ("z", 1))


def test_undefined_name_parser_is_conservative() -> None:
    assert undefined_name("'value' is undefined") == "value"
    assert undefined_name("other failure") is None
