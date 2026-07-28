from __future__ import annotations

from copy import deepcopy

from dryv.api import CancellationToken
from dryv.plugins import PluginCategory, PluginTrust
from dryv.ports import RenderRequest, TemplateEngine
from dryv.testing import assert_template_engine_conformance
from dryv.versions import IR_API_VERSION, PLUGIN_API_VERSION
from dryv_template_jinja import JinjaTemplateEngine


def test_engine_implements_public_protocol() -> None:
    engine = JinjaTemplateEngine()
    assert isinstance(engine, TemplateEngine)


def test_shared_conformance_passes() -> None:
    engine = JinjaTemplateEngine()
    assert_template_engine_conformance(
        engine,
        RenderRequest(
            template_id="hello.txt.jinja",
            source="Hello {{ name }}",
            context=(("name", "World"),),
        ),
    )


def test_descriptor_is_truthful_and_compatible() -> None:
    descriptor = JinjaTemplateEngine().plugin
    assert descriptor.id == "jinja"
    assert descriptor.category is PluginCategory.TEMPLATE_ENGINE
    assert descriptor.distribution == "dryv-template-jinja"
    assert descriptor.api_version == PLUGIN_API_VERSION
    assert descriptor.ir_version == IR_API_VERSION
    assert descriptor.trust is PluginTrust.EXECUTABLE
    assert descriptor.capabilities == tuple(sorted(set(descriptor.capabilities)))
    assert "named_outputs" not in descriptor.capabilities
    assert "filesystem" not in " ".join(descriptor.capabilities)


def test_suffixes_are_exact_sorted_and_unique() -> None:
    assert JinjaTemplateEngine().suffixes == (".j2", ".jinja", ".jinja2")


def test_request_context_and_partials_remain_unchanged() -> None:
    context = (("items", ("a", "b")),)
    partials = (("partial.jinja", "{{ items | join(',') }}"),)
    before_context = deepcopy(context)
    before_partials = deepcopy(partials)
    request = RenderRequest(
        "root.jinja",
        '{% include "partial.jinja" %}',
        context,
        partials,
    )
    result = JinjaTemplateEngine().render(request, CancellationToken())
    assert result.content == "a,b"
    assert context == before_context
    assert partials == before_partials


def test_failure_returns_error_diagnostics_not_exception() -> None:
    result = JinjaTemplateEngine().render(
        RenderRequest("root.jinja", "{{ missing }}"), CancellationToken()
    )
    assert result.content is None
    assert result.diagnostics.has_errors
