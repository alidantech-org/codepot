from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from dryv.api import CancellationToken
from dryv.ports import RenderRequest
from dryv_template_jinja import (
    HelperDescriptor,
    HelperKind,
    JinjaEngineRules,
    JinjaTemplateEngine,
)


def render(engine: JinjaTemplateEngine, request: RenderRequest):
    return engine.render(request, CancellationToken())


def test_cache_hit_and_explicit_clear() -> None:
    engine = JinjaTemplateEngine()
    request = RenderRequest("root.jinja", "Hello {{ name }}", (("name", "World"),))
    assert render(engine, request).content == "Hello World"
    assert render(engine, request).content == "Hello World"
    assert engine.cache_stats.entries == 1
    assert engine.cache_stats.hits >= 1
    engine.clear_cache()
    assert engine.cache_stats.entries == 0


def test_relevant_sources_invalidate_but_unused_partials_do_not() -> None:
    engine = JinjaTemplateEngine()
    base = RenderRequest(
        "root.jinja",
        '{% include "used.jinja" %}',
        (),
        (("unused.jinja", "one"), ("used.jinja", "used")),
    )
    unused_changed = RenderRequest(
        "root.jinja",
        '{% include "used.jinja" %}',
        (),
        (("unused.jinja", "two"), ("used.jinja", "used")),
    )
    used_changed = RenderRequest(
        "root.jinja",
        '{% include "used.jinja" %}',
        (),
        (("unused.jinja", "two"), ("used.jinja", "changed")),
    )
    assert engine.compilation_identity(base) == engine.compilation_identity(unused_changed)
    assert engine.compilation_identity(base) != engine.compilation_identity(used_changed)


def test_rules_and_helper_versions_invalidate_identity() -> None:
    request = RenderRequest("root.jinja", "{{ value | custom }}", (("value", "x"),))

    def custom(value: object) -> object:
        return value

    first = JinjaTemplateEngine(
        rules=JinjaEngineRules(trim_blocks=True),
        helpers=(HelperDescriptor("custom", "custom", HelperKind.FILTER, "1", custom),),
    )
    second = JinjaTemplateEngine(
        rules=JinjaEngineRules(trim_blocks=False),
        helpers=(HelperDescriptor("custom", "custom", HelperKind.FILTER, "2", custom),),
    )
    assert first.compilation_identity(request) != second.compilation_identity(request)


def test_bounded_eviction() -> None:
    engine = JinjaTemplateEngine(rules=JinjaEngineRules(cache_entries=2))
    for index in range(3):
        result = render(engine, RenderRequest(f"{index}.jinja", str(index)))
        assert result.content == str(index)
    assert engine.cache_stats.entries == 2
    assert engine.cache_stats.evictions == 1


def test_failed_compilation_does_not_poison_later_valid_render() -> None:
    engine = JinjaTemplateEngine()
    failed = render(engine, RenderRequest("root.jinja", "{% if %}"))
    assert failed.content is None
    valid = render(engine, RenderRequest("root.jinja", "valid"))
    assert valid.content == "valid"
    assert engine.cache_stats.entries == 1


def test_concurrent_rendering_is_deterministic() -> None:
    engine = JinjaTemplateEngine()
    request = RenderRequest(
        "root.jinja",
        "{% for item in items %}{{ item }}{% endfor %}",
        (("items", tuple(range(20))),),
    )
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = tuple(executor.map(lambda _: render(engine, request), range(100)))
    assert {result.content for result in results} == {"".join(map(str, range(20)))}
    assert all(not result.diagnostics.has_errors for result in results)
