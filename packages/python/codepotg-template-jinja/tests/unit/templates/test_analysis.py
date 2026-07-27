from __future__ import annotations

import pytest

from codepotg.api import CancellationToken
from codepotg.ports import RenderRequest
from codepotg_template_jinja import JinjaEngineRules
from codepotg_template_jinja.helpers import HelperRegistry
from codepotg_template_jinja.sandbox import create_environment
from codepotg_template_jinja.templates import (
    ImmutableRegistryLoader,
    TemplateAnalysisError,
    TemplateRegistry,
    analyze_dependencies,
)


def analyze(source: str, partials: tuple[tuple[str, str], ...] = (), *, depth: int = 32):
    rules = JinjaEngineRules(max_include_depth=depth)
    registry = TemplateRegistry.create(RenderRequest("root.jinja", source, (), partials), rules)
    environment = create_environment(
        loader=ImmutableRegistryLoader(registry.selected(registry.partial_ids)),
        rules=rules,
        helpers=HelperRegistry.create(),
        cache_size=0,
    )
    return analyze_dependencies(environment, registry, rules, CancellationToken())


def test_static_dependency_kinds_are_collected() -> None:
    source = (
        '{% extends "base.jinja" %}'
        '{% include "header.jinja" %}'
        '{% import "macros.jinja" as m %}'
        '{% from "fields.jinja" import field %}'
    )
    partials = (
        ("base.jinja", "base"),
        ("fields.jinja", "{% macro field() %}x{% endmacro %}"),
        ("header.jinja", "header"),
        ("macros.jinja", "{% macro x() %}x{% endmacro %}"),
    )
    result = analyze(source, partials)
    assert result.reachable_partial_ids == tuple(name for name, _ in partials)
    assert {edge.kind.value for edge in result.edges} == {
        "extends",
        "from_import",
        "import",
        "include",
    }


@pytest.mark.parametrize(
    "source",
    [
        "{% include name %}",
        "{% include ['a.jinja', 'b.jinja'] %}",
        "{% import name as macros %}",
        "{% include 'missing.jinja' ignore missing %}",
    ],
)
def test_dynamic_or_nondeterministic_dependencies_are_rejected(source: str) -> None:
    with pytest.raises(TemplateAnalysisError) as captured:
        analyze(source)
    assert captured.value.code == "JINJA_INCLUDE_DYNAMIC"


def test_missing_dependency_is_rejected() -> None:
    with pytest.raises(TemplateAnalysisError) as captured:
        analyze('{% include "missing.jinja" %}')
    assert captured.value.code == "JINJA_INCLUDE_MISSING"


def test_cycle_is_rejected_with_stable_stack() -> None:
    with pytest.raises(TemplateAnalysisError) as captured:
        analyze('{% include "a.jinja" %}', (("a.jinja", '{% include "root.jinja" %}'),))
    assert captured.value.code == "JINJA_INCLUDE_CYCLE"
    assert dict(captured.value.details)["include_stack"] == "root.jinja -> a.jinja -> root.jinja"


def test_include_depth_is_enforced() -> None:
    with pytest.raises(TemplateAnalysisError) as captured:
        analyze(
            '{% include "a.jinja" %}',
            (("a.jinja", '{% include "b.jinja" %}'), ("b.jinja", "done")),
            depth=1,
        )
    assert captured.value.code == "JINJA_INCLUDE_DEPTH"


def test_ast_node_limit_is_enforced() -> None:
    registry = TemplateRegistry.create(
        RenderRequest(
            template_id="root.jinja",
            source="{% for item in items %}{{ item }}{% endfor %}",
            context=(),
        ),
        JinjaEngineRules(),
    )
    rules = JinjaEngineRules(max_ast_nodes=2)
    environment = create_environment(
        loader=ImmutableRegistryLoader(registry.selected(registry.partial_ids)),
        rules=rules,
        helpers=HelperRegistry.create(),
        cache_size=0,
    )
    with pytest.raises(TemplateAnalysisError) as raised:
        analyze_dependencies(
            environment,
            registry,
            rules,
            CancellationToken(),
        )
    assert raised.value.code == "JINJA_TEMPLATE_TOO_LARGE"
