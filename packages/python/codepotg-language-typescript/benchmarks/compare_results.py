from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print(
            json.dumps(
                {"error": "usage: compare_results.py V1_JSON V2_JSON"},
                sort_keys=True,
            )
        )
        return 2

    v1 = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    v2 = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    if v1.get("runner") != "v1" or v2.get("runner") != "v2":
        print(
            json.dumps(
                {"error": "runner identities do not match v1/v2"},
                sort_keys=True,
            )
        )
        return 3

    v1_results = {
        item["original"]: item for item in v1.get("identifier_results", ())
    }
    v2_results = {
        item["original"]: item for item in v2.get("identifier_results", ())
    }
    comparisons = []
    for original in sorted(set(v1_results) & set(v2_results)):
        old = v1_results[original]
        new = v2_results[original]
        reason = None
        if old["changed"]:
            reason = (
                "v1 transformed the authored candidate; v2 preserved it and "
                "returned diagnostics"
            )
        comparisons.append(
            {
                "non_equivalent_reason": reason,
                "original": original,
                "v1_changed": old["changed"],
                "v2_accepted": new["accepted"],
                "v2_diagnostic_codes": new["diagnostic_codes"],
            }
        )

    print(
        json.dumps(
            {
                "comparisons": comparisons,
                "v1_measurements": v1.get("measurements", {}),
                "v2_measurements": v2.get("measurements", {}),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
