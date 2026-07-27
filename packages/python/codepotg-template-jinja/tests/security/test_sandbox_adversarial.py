from __future__ import annotations

import pytest

from codepotg_template_jinja import JinjaTemplateEngine

from tests.conftest import render


@pytest.mark.parametrize(
    "source",
    [
        "{{ value.__class__ }}",
        "{{ value.__class__.__mro__ }}",
        "{{ value.__class__.__subclasses__() }}",
        "{{ cycler.__init__.__globals__.os }}",
        "{{ namespace.__init__.__globals__ }}",
        "{{ lipsum.__globals__ }}",
        "{{ [].__class__ }}",
        "{{ config.items() }}",
        "{{ callable_from_context() }}",
        "{{ (1 / 0).__traceback__ }}",
    ],
)
def test_common_sandbox_escape_payloads_fail_closed(source: str) -> None:
    context: tuple[tuple[str, object], ...] = (
        ("config", (("safe", "value"),)),
        ("value", "text"),
    )
    if "callable_from_context" in source:
        context = (("callable_from_context", lambda: "escaped"),)
    result = render(JinjaTemplateEngine(), source, context=context)
    assert result.content is None
    assert result.diagnostics.has_errors
    serialized = str(result.diagnostics.errors[0])
    assert "Traceback" not in serialized
    assert "0x" not in serialized


@pytest.mark.parametrize(
    "source",
    [
        "{% include variable %}",
        "{% include '../secret' %}",
        "{% import variable as x %}",
        "{% from variable import x %}",
    ],
)
def test_dynamic_or_traversing_dependencies_are_denied(source: str) -> None:
    result = render(JinjaTemplateEngine(), source, context=(("variable", "safe.jinja"),))
    assert result.content is None
    assert result.diagnostics.has_errors
    assert result.diagnostics.errors[0].code in {
        "JINJA_INCLUDE_DYNAMIC",
        "JINJA_PARTIAL_INVALID",
    }


@pytest.mark.parametrize(
    "name",
    [
        "os",
        "sys",
        "subprocess",
        "pathlib",
        "builtins",
        "open",
        "eval",
        "exec",
        "compile",
        "globals",
        "locals",
        "vars",
        "getattr",
        "setattr",
        "delattr",
        "importlib",
    ],
)
def test_python_and_host_roots_are_not_globals(name: str) -> None:
    result = render(JinjaTemplateEngine(), "{{ " + name + " }}")
    assert result.content is None
    assert result.diagnostics.errors[0].code == "JINJA_UNDEFINED"


def test_private_safe_record_keys_cannot_be_reached_by_item_or_attribute() -> None:
    result = render(
        JinjaTemplateEngine(),
        "{{ value.__class__ }} {{ value['__class__'] }}",
        context=(("value", (("safe", "ok"),)),),
    )
    assert result.content is None
    assert result.diagnostics.has_errors
