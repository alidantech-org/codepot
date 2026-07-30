from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_v2_benchmark_has_required_neutral_cases() -> None:
    module = _load("dryv_jinja_benchmark_v2", PACKAGE_ROOT / "benchmarks/run_v2_engine.py")
    names = tuple(case.name for case in module.cases())
    assert names == (
        "scalar_interpolation",
        "nested_mapping_lookup",
        "conditional_branches",
        "loop_100",
        "loop_1000",
        "macro_invocation",
        "single_include",
        "include_chain_8",
        "inheritance",
        "large_output",
        "strict_undefined_failure",
        "syntax_failure",
        "warm_100",
    )
    assert module.MEASURED_ITERATIONS >= 7


def test_v1_and_v2_runners_remain_separate() -> None:
    v1 = (PACKAGE_ROOT / "benchmarks/run_v1_baseline.py").read_text(encoding="utf-8")
    v2 = (PACKAGE_ROOT / "benchmarks/run_v2_engine.py").read_text(encoding="utf-8")
    assert "dryv_template_jinja" not in v1
    assert "emission.templates.renderer" not in v2
