from __future__ import annotations

import hashlib
import json
import statistics
import sys
import time
from dataclasses import dataclass
from typing import Any

from codepotg.api import CancellationToken
from codepotg.ports import RenderRequest
from codepotg_template_jinja import JinjaTemplateEngine

MEASURED_ITERATIONS = 7


@dataclass(frozen=True, slots=True)
class Case:
    name: str
    source: str
    context: tuple[tuple[str, object], ...] = ()
    partials: tuple[tuple[str, str], ...] = ()
    repeats: int = 1
    expects_error: bool = False


def cases() -> tuple[Case, ...]:
    return (
        Case("scalar_interpolation", "Hello {{ name }}", (("name", "World"),)),
        Case(
            "nested_mapping_lookup",
            "{{ user.profile.display_name }}",
            (("user", (("profile", (("display_name", "Ada"),)),)),),
        ),
        Case(
            "conditional_branches",
            "{% if enabled %}enabled{% else %}disabled{% endif %}",
            (("enabled", True),),
        ),
        Case(
            "loop_100",
            "{% for item in items %}{{ item }},\n{% endfor %}",
            (("items", tuple(range(100))),),
        ),
        Case(
            "loop_1000",
            "{% for item in items %}{{ item }},\n{% endfor %}",
            (("items", tuple(range(1_000))),),
        ),
        Case(
            "macro_invocation",
            "{% macro wrap(value) %}[{{ value }}]{% endmacro %}{{ wrap(name) }}",
            (("name", "value"),),
        ),
        Case(
            "single_include",
            'before:{% include "partial.jinja" %}:after',
            (),
            (("partial.jinja", "included"),),
        ),
        Case(
            "include_chain_8",
            '{% include "level-1.jinja" %}',
            (),
            tuple(
                (
                    f"level-{index}.jinja",
                    f'{index}>{{% include "level-{index + 1}.jinja" %}}' if index < 8 else "8>done",
                )
                for index in range(1, 9)
            ),
        ),
        Case(
            "inheritance",
            '{% extends "base.jinja" %}{% block body %}child+{{ super() }}{% endblock %}',
            (),
            (("base.jinja", "{% block body %}base{% endblock %}"),),
        ),
        Case(
            "large_output",
            "{% for item in items %}abcdefghij{{ item }}\n{% endfor %}",
            (("items", tuple(range(20_000))),),
        ),
        Case("strict_undefined_failure", "{{ missing }}", expects_error=True),
        Case("syntax_failure", "{% if %}", expects_error=True),
        Case("warm_100", "{{ left }}-{{ right }}", (("left", "a"), ("right", "b")), repeats=100),
    )


def _rss_bytes() -> int | None:
    try:
        import resource

        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return int(value if sys.platform == "darwin" else value * 1_024)
    except (ImportError, OSError, ValueError):
        return None


def _render(engine: JinjaTemplateEngine, request: RenderRequest, repeats: int) -> Any:
    result = None
    for _ in range(repeats):
        result = engine.render(request, CancellationToken())
    return result


def _duration(engine: JinjaTemplateEngine, request: RenderRequest, repeats: int) -> tuple[int, Any]:
    start = time.perf_counter_ns()
    result = _render(engine, request, repeats)
    return time.perf_counter_ns() - start, result


def run_case(case: Case) -> dict[str, object]:
    request = RenderRequest(
        template_id=f"{case.name}.jinja",
        source=case.source,
        context=case.context,
        partials=case.partials,
    )
    _render(JinjaTemplateEngine(), request, case.repeats)
    cold_ns: list[int] = []
    cold_result = None
    for _ in range(MEASURED_ITERATIONS):
        engine = JinjaTemplateEngine()
        duration, cold_result = _duration(engine, request, case.repeats)
        cold_ns.append(duration)
    warm_engine = JinjaTemplateEngine()
    _render(warm_engine, request, case.repeats)
    warm_ns: list[int] = []
    warm_result = None
    for _ in range(MEASURED_ITERATIONS):
        duration, warm_result = _duration(warm_engine, request, case.repeats)
        warm_ns.append(duration)
    assert cold_result is not None and warm_result is not None
    assert cold_result == warm_result
    content = warm_result.content
    output = content if content is not None else ""
    first_error = warm_result.diagnostics.errors[0] if warm_result.diagnostics.has_errors else None
    return {
        "cache": {
            "entries": warm_engine.cache_stats.entries,
            "evictions": warm_engine.cache_stats.evictions,
            "hits": warm_engine.cache_stats.hits,
            "misses": warm_engine.cache_stats.misses,
        },
        "cold_ns": cold_ns,
        "cold_median_ns": int(statistics.median(cold_ns)),
        "cold_max_ns": max(cold_ns),
        "error_code": first_error.code if first_error is not None else None,
        "expects_error": case.expects_error,
        "name": case.name,
        "output_bytes": len(output.encode("utf-8")),
        "output_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
        "peak_rss_bytes": _rss_bytes(),
        "repeats_per_iteration": case.repeats,
        "warm_ns": warm_ns,
        "warm_median_ns": int(statistics.median(warm_ns)),
        "warm_max_ns": max(warm_ns),
    }


def main() -> int:
    payload = {
        "engine": "codepotg-template-jinja-v2",
        "iterations": MEASURED_ITERATIONS,
        "python": sys.version.split()[0],
        "results": [run_case(case) for case in cases()],
        "warmups": 1,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
