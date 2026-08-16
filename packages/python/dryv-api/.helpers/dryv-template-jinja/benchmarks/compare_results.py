from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"benchmark payload must be an object: {path}")
    return value


def _by_name(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    rows = payload.get("results")
    if not isinstance(rows, list):
        raise ValueError("benchmark payload requires a results list")
    return {str(row["name"]): row for row in rows if isinstance(row, dict)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare isolated Dryv Jinja benchmark JSON.")
    parser.add_argument("v1", type=Path)
    parser.add_argument("v2", type=Path)
    args = parser.parse_args()

    v1 = _by_name(_load(args.v1))
    v2 = _by_name(_load(args.v2))
    names = sorted(set(v1) | set(v2))
    rows: list[dict[str, object]] = []
    for name in names:
        left = v1.get(name)
        right = v2.get(name)
        comparable = left is not None and right is not None
        output_equal = (
            comparable
            and left.get("output_sha256") == right.get("output_sha256")
            and left.get("output_bytes") == right.get("output_bytes")
        )
        rows.append(
            {
                "case": name,
                "cold_median_v1_ns": left.get("cold_median_ns") if left else None,
                "cold_median_v2_ns": right.get("cold_median_ns") if right else None,
                "comparable": comparable,
                "output_equal": output_equal,
                "warm_median_v1_ns": left.get("warm_median_ns") if left else None,
                "warm_median_v2_ns": right.get("warm_median_ns") if right else None,
            }
        )
    print(json.dumps({"comparisons": rows}, indent=2, sort_keys=True))
    return 0 if all(
        row["output_equal"]
        for row in rows
        if row["comparable"] and "failure" not in str(row["case"])
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
