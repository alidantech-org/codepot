"""Profile CodepotG stages against a real OpenAPI document.

Run speed and process-memory tracing without ``--full``:

    python scripts/profile_memory.py tests/fixtures/openapi.json --emit
    python scripts/profile_memory.py tests/fixtures/openapi.yaml --emit

Use ``--full`` only for allocation diagnostics. Ten-frame ``tracemalloc`` tracking
intentionally adds substantial CPU overhead and is not a production speed benchmark.
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import tempfile
from dataclasses import replace
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PACKAGE_ROOT / "src"
for value in (str(SOURCE_ROOT), str(PACKAGE_ROOT)):
    if value not in sys.path:
        sys.path.insert(0, value)

from app.models import EmitInput  # noqa: E402
from app.workflows.normalization import required_normalized_roots  # noqa: E402
from app.workflows.template_paths import resolve_template_root  # noqa: E402
from core.memory_trace import MemoryTrace  # noqa: E402
from emission.bounded_graph_engine import emit_bounded_graph  # noqa: E402
from emission.legacy_queued_engine import emit_legacy_queued as emit_legacy  # noqa: E402
from emission.paths.config_loader import load_path_config  # noqa: E402
from emission.templates.renderer import clear_environment_cache  # noqa: E402
from inference.engine import InferenceEngine  # noqa: E402
from inference.generation_contract import build_generation_contract  # noqa: E402
from languages.discovery import resolve_language_adapter  # noqa: E402
from openapi.jsonl import compile_openapi_source_jsonl  # noqa: E402
from openapi.loader import load_openapi_document  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Trace CodepotG speed and memory by generation stage."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("--language", default="debug")
    parser.add_argument("--templates", type=Path)
    parser.add_argument(
        "--emit",
        action="store_true",
        help="Render and write the planned outputs after template planning.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help=(
            "Enable ten-frame tracemalloc diagnostics. This is intentionally slow "
            "and must not be used as a speed benchmark."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print snapshots as JSON after the readable report.",
    )
    args = parser.parse_args()

    source = args.input.expanduser().resolve()
    if not source.is_file():
        parser.error(f"OpenAPI input does not exist: {source}")
    if args.full:
        print(
            "warning: --full enables expensive allocation tracing; "
            "rerun without --full for speed measurements",
            file=sys.stderr,
        )

    with tempfile.TemporaryDirectory(prefix="codepotg-memory-") as directory:
        root = Path(directory)
        cache = root / "cache"
        output = root / "output"
        trace = MemoryTrace(
            enabled=True,
            trace_allocations=args.full,
            output_path=None,
        )
        try:
            trace.snapshot("start")
            jsonl = compile_openapi_source_jsonl(source, cache)
            trace.snapshot("jsonl_ready")

            compatibility_input = jsonl.compatibility_path or source
            document = load_openapi_document(compatibility_input)
            trace.snapshot("document_loaded")

            graph = InferenceEngine().infer(document, copy_raw=False)
            del document
            trace.snapshot("graph_inferred")

            adapter = resolve_language_adapter(args.language)
            template_root = resolve_template_root(
                adapter=adapter,
                templates_path=args.templates,
            )
            normalized_roots = required_normalized_roots(template_root)
            print(
                "normalized roots: "
                + (", ".join(sorted(normalized_roots)) if normalized_roots else "none")
            )
            contract = build_generation_contract(
                graph,
                normalized_roots=normalized_roots,
            )
            del graph
            trace.snapshot("contract_built")

            request = EmitInput(
                input_path=source,
                language=args.language,
                output_path=output,
                templates_path=args.templates,
                dry_run=not args.emit,
            )
            template_contract = adapter.build_template_contract(
                api=contract,
                output_path=output,
                template_root=template_root,
                dry_run=request.dry_run,
                frontend=request.frontend,
                progress=None,
            )
            source_meta = jsonl.manifest.source
            source_size = int(
                source_meta.get("originalSize", source_meta.get("size", source.stat().st_size))
            )
            template_contract = replace(
                template_contract,
                emit=replace(
                    template_contract.emit,
                    meta={
                        **template_contract.emit.meta,
                        "jsonl_cache": str(jsonl.cache_dir),
                        "jsonl_reused": jsonl.reused,
                        "jsonl_source_size": source_size,
                        "jsonl_index_backend": "sqlite",
                        "normalized_roots": tuple(sorted(normalized_roots)),
                    },
                ),
            )
            trace.snapshot("template_contract_built")

            if args.emit:
                path_config = load_path_config(template_root)
                if path_config.uses_graph:
                    emission = emit_bounded_graph(template_contract)
                else:
                    emission = emit_legacy(template_contract)
                trace.snapshot("emission_complete")
                print(
                    "outputs: "
                    f"planned={len(emission.plan.files)}, "
                    f"created={len(emission.write_result.created)}, "
                    f"updated={len(emission.write_result.updated)}, "
                    f"unchanged={len(emission.write_result.unchanged)}"
                )
                if emission.queue_stats is not None:
                    stats = emission.queue_stats
                    print(
                        "write queues: "
                        f"files_peak={stats.pending_files_high_water}, "
                        f"bytes_peak={stats.pending_bytes_high_water}, "
                        f"waits={stats.queue_waits}, "
                        f"batches={stats.batches_written}, "
                        f"batch_files_peak={stats.batch_files_high_water}, "
                        f"written={stats.files_written}"
                    )
                del emission

            del template_contract
            del contract
            del jsonl
            clear_environment_cache()
            gc.collect()
            trace.snapshot("released")

            previous_elapsed = 0.0
            for snapshot in trace.snapshots:
                stage_ms = snapshot.elapsed_ms - previous_elapsed
                previous_elapsed = snapshot.elapsed_ms
                print(f"{snapshot.summary()}, stage_time={stage_ms:.1f}ms")
            if args.json:
                rows = []
                previous_elapsed = 0.0
                for snapshot in trace.snapshots:
                    row = snapshot.to_json()
                    row["stage_elapsed_ms"] = snapshot.elapsed_ms - previous_elapsed
                    previous_elapsed = snapshot.elapsed_ms
                    rows.append(row)
                print(json.dumps(rows, indent=2, sort_keys=True))
        finally:
            clear_environment_cache()
            trace.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
