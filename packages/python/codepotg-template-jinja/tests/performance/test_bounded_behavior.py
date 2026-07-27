from __future__ import annotations

import time

import pytest

from codepotg.api import CancellationToken
from codepotg.ports import RenderRequest
from codepotg_template_jinja import JinjaEngineRules, JinjaTemplateEngine

from tests.conftest import diagnostic_code, render


@pytest.mark.performance
def test_large_but_bounded_loop_renders_deterministically() -> None:
    engine = JinjaTemplateEngine(rules=JinjaEngineRules(max_render_bytes=100_000))
    context = (("items", tuple(range(1_000))),)
    first = render(engine, "{% for item in items %}{{ item }},\n{% endfor %}", context=context)
    second = render(engine, "{% for item in items %}{{ item }},\n{% endfor %}", context=context)
    assert first == second
    assert first.content is not None
    assert len(first.content.encode("utf-8")) < 100_000


@pytest.mark.performance
def test_output_limit_stops_oversized_render() -> None:
    engine = JinjaTemplateEngine(rules=JinjaEngineRules(max_render_bytes=1_024))
    result = render(
        engine,
        "{% for item in items %}0123456789{% endfor %}",
        context=(("items", tuple(range(1_000))),),
    )
    assert diagnostic_code(result) == "JINJA_RENDER_LIMIT"


@pytest.mark.performance
def test_warm_render_has_cache_hit_without_time_threshold() -> None:
    engine = JinjaTemplateEngine()
    request = RenderRequest("root.jinja", "Hello {{ name }}", (("name", "World"),))
    start = time.perf_counter()
    first = engine.render(request, CancellationToken())
    cold = time.perf_counter() - start
    start = time.perf_counter()
    second = engine.render(request, CancellationToken())
    warm = time.perf_counter() - start
    assert first == second
    assert engine.cache_stats.hits >= 1
    assert cold >= 0 and warm >= 0
