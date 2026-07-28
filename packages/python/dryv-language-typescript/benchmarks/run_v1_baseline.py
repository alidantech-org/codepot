from __future__ import annotations

import json
import statistics
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

try:
    import resource
except ImportError:  # pragma: no cover - Windows benchmark hosts
    resource = None  # type: ignore[assignment]

RUNS = 7
BATCH = 10_000


def _measure(operation: Callable[[int], None]) -> dict[str, Any]:
    operation(0)
    durations: list[float] = []
    for _ in range(RUNS):
        start = time.perf_counter()
        for index in range(BATCH):
            operation(index)
        durations.append(time.perf_counter() - start)

    total_operations = RUNS * BATCH
    return {
        "batch_size": BATCH,
        "maximum_seconds": max(durations),
        "median_seconds": statistics.median(durations),
        "minimum_seconds": min(durations),
        "operations_per_second": total_operations / sum(durations),
        "peak_rss_kib": (
            None if resource is None else resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        ),
        "runs": RUNS,
        "total_operations": total_operations,
    }


def main() -> int:
    try:
        from languages.typescript.names import safe_ts_identifier
    except ImportError as error:
        print(
            json.dumps(
                {
                    "error": str(error),
                    "runner": "v1",
                    "status": "old_dryv_not_installed",
                },
                sort_keys=True,
            )
        )
        return 2

    cases = json.loads(Path(__file__).with_name("cases.json").read_text(encoding="utf-8"))
    results = []
    for original in cases["identifiers"]:
        start = time.perf_counter_ns()
        transformed = safe_ts_identifier(original)
        results.append(
            {
                "changed": transformed != original,
                "elapsed_ns": time.perf_counter_ns() - start,
                "original": original,
                "transformed": transformed,
            }
        )

    def identifiers(index: int) -> None:
        safe_ts_identifier(cases["identifiers"][index % len(cases["identifiers"])])

    print(
        json.dumps(
            {
                "identifier_results": results,
                "measurements": {"identifier_transformation": _measure(identifiers)},
                "non_equivalent_reason": (
                    "v1 repairs candidates; v2 diagnoses candidates without mutation"
                ),
                "runner": "v1",
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
