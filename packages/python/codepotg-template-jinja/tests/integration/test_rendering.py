from __future__ import annotations

import pytest

from codepotg_template_jinja import JinjaEngineRules, JinjaTemplateEngine

from tests.conftest import diagnostic_code, render


def test_plain_interpolation_loop_and_conditionals(engine: JinjaTemplateEngine) -> None:
    result = render(
        engine,
        "{% if enabled %}{% for item in items %}{{ item }}{% if not loop.last %}, {% endif %}{% endfor %}{% endif %}",
        context=(("enabled", True), ("items", ("a", "b", "c"))),
    )
    assert result.content == "a, b, c"


@pytest.mark.parametrize(
    "source",
    (
        "{% for item in items %}{{ loop.cycle('odd', 'even') }}{% endfor %}",
        "{% for item in items %}{{ loop.changed(item) }}{% endfor %}",
    ),
)
def test_loop_state_callables_remain_deliberately_denied(
    engine: JinjaTemplateEngine,
    source: str,
) -> None:
    result = render(engine, source, context=(("items", ("a", "b")),))
    assert diagnostic_code(result) == "JINJA_CALLABLE_DENIED"


def test_template_defined_macro_runs(engine: JinjaTemplateEngine) -> None:
    result = render(
        engine,
        "{% macro wrap(value) %}[{{ value }}]{% endmacro %}{{ wrap(name) }}",
        context=(("name", "demo"),),
    )
    assert result.content == "[demo]"


def test_static_include_and_nested_include(engine: JinjaTemplateEngine) -> None:
    result = render(
        engine,
        'A{% include "a.jinja" %}D',
        partials=(
            ("a.jinja", 'B{% include "b.jinja" %}'),
            ("b.jinja", "C"),
        ),
    )
    assert result.content == "ABCD"


def test_static_inheritance_with_super(engine: JinjaTemplateEngine) -> None:
    result = render(
        engine,
        '{% extends "base.jinja" %}{% block body %}child+{{ super() }}{% endblock %}',
        partials=(("base.jinja", "{% block body %}base{% endblock %}"),),
    )
    assert result.content == "child+base"


def test_static_import_and_from_import(engine: JinjaTemplateEngine) -> None:
    partials = (
        (
            "macros.jinja",
            "{% macro wrap(value) %}<{{ value }}>{% endmacro %}{% macro suffix(value) %}{{ value }}!{% endmacro %}",
        ),
    )
    imported = render(
        engine,
        '{% import "macros.jinja" as m %}{{ m.wrap(name) }}',
        context=(("name", "A"),),
        partials=partials,
    )
    from_imported = render(
        engine,
        '{% from "macros.jinja" import suffix %}{{ suffix(name) }}',
        context=(("name", "A"),),
        partials=partials,
    )
    assert imported.content == "<A>"
    assert from_imported.content == "A!"


def test_strict_undefined_returns_stable_diagnostic(engine: JinjaTemplateEngine) -> None:
    result = render(engine, "{{ missing }}")
    assert diagnostic_code(result) == "JINJA_UNDEFINED"
    assert dict(result.diagnostics.errors[0].details)["undefined_name"] == "missing"


def test_whitespace_defaults_and_trailing_newline(engine: JinjaTemplateEngine) -> None:
    result = render(engine, "start\n{% if true %}\nvalue\n{% endif %}\n")
    assert result.content == "start\nvalue\n"


def test_custom_newline_sequence() -> None:
    engine = JinjaTemplateEngine(rules=JinjaEngineRules(newline_sequence="\r\n"))
    result = render(engine, "a\r\nb\n")
    assert result.content == "a\r\nb\r\n"


def test_syntax_error_is_source_spanned(engine: JinjaTemplateEngine) -> None:
    result = render(engine, "line1\n{% if %}\n")
    assert diagnostic_code(result) == "JINJA_SYNTAX"
    diagnostic = result.diagnostics.errors[0]
    assert diagnostic.span is not None
    assert diagnostic.span.start.line == 2


def test_missing_include_diagnostic_names_dependency(engine: JinjaTemplateEngine) -> None:
    result = render(engine, '{% include "missing.jinja" %}')
    assert diagnostic_code(result) == "JINJA_INCLUDE_MISSING"
    assert dict(result.diagnostics.errors[0].details)["dependency_id"] == "missing.jinja"


def test_root_source_type_rejection_uses_template_diagnostic(
    engine: JinjaTemplateEngine,
) -> None:
    result = render(engine, object())  # type: ignore[arg-type]
    assert diagnostic_code(result) == "JINJA_TEMPLATE_INVALID"


def test_context_rejection_is_structured(engine: JinjaTemplateEngine) -> None:
    result = render(engine, "{{ value }}", context=(("value", object()),))
    assert diagnostic_code(result) == "JINJA_CONTEXT_UNSAFE"


def test_render_limit_is_checked_while_streaming() -> None:
    engine = JinjaTemplateEngine(rules=JinjaEngineRules(max_render_bytes=5))
    result = render(engine, "{{ items | join('') }}", context=(("items", ("abc", "def")),))
    assert diagnostic_code(result) == "JINJA_RENDER_LIMIT"
    assert result.content is None