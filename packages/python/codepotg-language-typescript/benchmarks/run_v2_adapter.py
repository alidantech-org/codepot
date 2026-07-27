from __future__ import annotations

import json
import statistics
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

try:
    import resource
except ImportError:  # pragma: no cover - Windows benchmark hosts
    resource = None  # type: ignore[assignment]

from codepotg.ports import (
    IdentifierRole,
    IdentifierValidationRequest,
    ModulePathRequest,
    OutputPathValidationRequest,
)

from codepotg_language_typescript import (
    AliasBinding,
    TypeScriptTargetAdapter,
    TypeScriptTargetOptions,
)

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
    cases = json.loads(Path(__file__).with_name("cases.json").read_text(encoding="utf-8"))
    adapter = TypeScriptTargetAdapter()
    alias_adapter = TypeScriptTargetAdapter(
        TypeScriptTargetOptions(
            aliases=(
                AliasBinding("@", "src"),
                AliasBinding("@domain", "src/domain"),
            )
        )
    )
    package_adapter = TypeScriptTargetAdapter(TypeScriptTargetOptions(package_name="example-sdk"))

    identifier_results = []
    for candidate in cases["identifiers"]:
        start = time.perf_counter_ns()
        diagnostics = adapter.validate_identifier(
            IdentifierValidationRequest(candidate, IdentifierRole.VALUE)
        )
        identifier_results.append(
            {
                "accepted": not diagnostics.has_errors,
                "diagnostic_codes": [item.code for item in diagnostics],
                "elapsed_ns": time.perf_counter_ns() - start,
                "original": candidate,
                "role": IdentifierRole.VALUE.value,
            }
        )

    def identifiers(index: int) -> None:
        candidate = cases["identifiers"][index % len(cases["identifiers"])]
        adapter.validate_identifier(IdentifierValidationRequest(candidate, IdentifierRole.VALUE))

    def output_paths(index: int) -> None:
        case = cases["output_paths"][index % len(cases["output_paths"])]
        adapter.validate_output_path(OutputPathValidationRequest(case["path"], case["target_id"]))

    def relative(index: int) -> None:
        case = cases["modules"][index % len(cases["modules"])]
        adapter.resolve_module_path(
            ModulePathRequest(
                case["current"],
                provider_artifact=case["provider"],
            )
        )

    def packages(index: int) -> None:
        package = cases["packages"][index % len(cases["packages"])]
        adapter.resolve_module_path(ModulePathRequest("src/service.ts", package_name=package))

    valid_explicit = tuple(
        item
        for item in cases["explicit_modules"]
        if "invalid" not in item and not item.startswith("'")
    )

    def explicit(index: int) -> None:
        adapter.resolve_module_path(
            ModulePathRequest(
                "src/service.ts",
                explicit_module=valid_explicit[index % len(valid_explicit)],
            )
        )

    def aliases(index: int) -> None:
        alias_adapter.resolve_module_path(
            ModulePathRequest(
                "app/service.ts",
                provider_artifact=f"src/domain/users/user_{index}.ts",
            )
        )

    def package_provider(index: int) -> None:
        package_adapter.resolve_module_path(
            ModulePathRequest(
                "src/service.ts",
                provider_artifact=f"src/types/user_{index}.ts",
                project_root="src",
            )
        )

    module_results = []
    for case in cases["modules"]:
        facts = adapter.resolve_module_path(
            ModulePathRequest(
                case["current"],
                provider_artifact=case["provider"],
            )
        )
        module_results.append(
            {
                "kind": facts.kind.value,
                "name": case["name"],
                "package_path": facts.package_path,
                "relative_path": facts.relative_path,
                "specifier": facts.specifier,
            }
        )

    output = {
        "identifier_results": identifier_results,
        "measurements": {
            "alias_resolution": _measure(aliases),
            "explicit_module_validation": _measure(explicit),
            "identifier_validation": _measure(identifiers),
            "output_path_validation": _measure(output_paths),
            "package_module_resolution": _measure(packages),
            "package_provider_resolution": _measure(package_provider),
            "relative_module_resolution": _measure(relative),
        },
        "module_results": module_results,
        "runner": "v2",
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
