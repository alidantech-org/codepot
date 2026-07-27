from __future__ import annotations

import hashlib
import json
import statistics
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

try:
    from emission.templates.renderer import clear_environment_cache, render_template
except ImportError:
    from src.emission.templates.renderer import clear_environment_cache, render_template

MEASURED_ITERATIONS = 7


@dataclass(frozen=True, slots=True)
class Case:
    name: str
    source: str
    context: dict[str, object]
    partials: tuple[tuple[str, str], ...] = ()
    repeats: int = 1
    expects_error: bool = False


def cases() -> tuple[Case, ...]:
    return (
        Case("scalar_interpolation", "Hello {{ name }}", {"name": "World"}),
        Case(
            "nested_mapping_lookup",
            "{{ user.profile.display_name }}",
            {"user": {"profile": {"display_name": "Ada"}}},
        ),
        Case(
            "conditional_branches",
            "{% if enabled %}enabled{% else %}disabled{% endif %}",
            {"enabled": True},
        ),
        Case(
            "loop_100",
            "{% for item in items %}{{ item }},\n{% endfor %}",
            {"items": tuple(range(100))},
        ),
        Case(
            "loop_1000",
            "{% for item in items %}{{ item }},\n{% endfor %}",
            {"items": tuple(range(1_000))},
        ),
        Case(
            "macro_invocation",
            "{% macro wrap(value) %}[{{ value }}]{% endmacro %}{{ wrap(name) }}",
            {"name": "value"},
        ),
        Case(
            "single_include",
            'before:{% include "partial.jinja" %}:after',
            {},
            (("partial.jinja", "included"),),
        ),
        Case(
            "include_chain_8",
            '{% include "level-1.jinja" %}',
            {},
            tuple(
                (
                    f"level-{index}.jinja",
                    (
                        f"{index}>{{% include \"level-{index + 1}.jinja\" %}}"
                        if index < 8
                        else "8>done"
                    ),
                )
                for index in range(1, 9)
            ),
        ),
        Case(
            "inheritance",
            '{% extends "base.jinja" %}{% block body %}child+{{ super() }}{% endblock %}',
            {},
            (("base.jinja", "{% block body %}base{% endblock %}"),),
        ),
        Case(
            "large_output",
            "{% for item in items %}abcdefghij{{ item }}\n{% endfor %}",
            {"items": tuple(range(20_000))},
        ),
        Case("strict_undefined_failure", "{{ missing }}", {}, expects_error=True),
        Case("syntax_failure", "{% if %}", {}, expects_error=True),
        Case(
            "warm_100",
            "{{ left }}-{{ right }}",
            {"left": "a", "right": "b"},
            repeats=100,
        ),
    )


def _rss_bytes() -> int | None:
    try:
        import resource

        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return int(value if sys.platform == "darwin" else value * 1_024)
    except (ImportError, OSError, ValueError):
        return None


def _write_case(root: Path, case: Case) -> Path:
    template = root / f"{case.name}.jinja"
    template.write_text(case.source, encoding="utf-8")
    for name, source in case.partials:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
    return template.relative_to(root)


def _render(root: Path, relative: Path, case: Case) -> tuple[str | None, str | None]:
    output: str | None = None
    error: str | None = None
    for _ in range(case.repeats):
        try:
            output = render_template(root, relative, case.context)
            error = None
        except Exception as exc:
            output = None
            error = type(exc).__name__
    return output, error


def _duration(
    root: Path,
    relative: Path,
    case: Case,
) -> tuple[int, tuple[str | None, str | None]]:
    start = time.perf_counter_ns()
    result = _render(root, relative, case)
    return time.perf_counter_ns() - start, result


def run_case(root: Path, case: Case) -> dict[str, object]:
    relative = _write_case(root, case)
    clear_environment_cache()
    _render(root, relative, case)

    cold_ns: list[int] = []
    cold_result: tuple[str | None, str | None] | None = None
    for _ in range(MEASURED_ITERATIONS):
        clear_environment_cache()
        duration, cold_result = _duration(root, relative, case)
        cold_ns.append(duration)

    clear_environment_cache()
    _render(root, relative, case)
    warm_ns: list[int] = []
    warm_result: tuple[str | None, str | None] | None = None
    for _ in range(MEASURED_ITERATIONS):
        duration, warm_result = _duration(root, relative, case)
        warm_ns.append(duration)

    assert cold_result is not None and warm_result is not None
    assert cold_result == warm_result
    output, error_type = warm_result
    rendered = output or ""
    return {
        "cache": {"warm_reuse_expected": True},
        "cold_ns": cold_ns,
        "cold_median_ns": int(statistics.median(cold_ns)),
        "cold_max_ns": max(cold_ns),
        "error_code": error_type,
        "expects_error": case.expects_error,
        "name": case.name,
        "output_bytes": len(rendered.encode("utf-8")),
        "output_sha256": hashlib.sha256(rendered.encode("utf-8")).hexdigest(),
        "peak_rss_bytes": _rss_bytes(),
        "repeats_per_iteration": case.repeats,
        "warm_ns": warm_ns,
        "warm_median_ns": int(statistics.median(warm_ns)),
        "warm_max_ns": max(warm_ns),
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="codepotg-v1-jinja-benchmark-") as directory:
        root = Path(directory)
        payload = {
            "engine": "codepotg-v1-renderer",
            "iterations": MEASURED_ITERATIONS,
            "python": sys.version.split()[0],
            "results": [run_case(root, case) for case in cases()],
            "warmups": 1,
        }
    clear_environment_cache()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
