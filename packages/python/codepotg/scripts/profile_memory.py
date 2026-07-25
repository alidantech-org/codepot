"""Profile CodepotG stages against a real OpenAPI document.

Run from packages/python/codepotg:

    python scripts/profile_memory.py tests/fixtures/openapi.json
    python scripts/profile_memory.py tests/fixtures/openapi.yaml --full --emit
"""

from __future__ import annotations

import argparse
import gc
import json
import os
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
from app.workflows.template_paths import resolve_template_root  # noqa: E402
from core.memory_trace import MemoryTrace  # noqa: E402
from emission.bounded_graph_engine import emit_bounded_graph  # noqa: E402
from emission.engine import emit as emit_legacy  # noqa: E402
from emission.paths.config_loader import load_path_config  # noqa: E402
from inference.engine import InferenceEngine  # noqa: E402
from inference.lossless_contract import build_api_contract  # noqa: E402
from languages.discovery import resolve_language_adapter  # noqa: E402
from openapi.jsonl import compile_openapi_source_jsonl  # noqa: E402
from openapi.loader import load_openapi_document  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Trace CodepotG time and memory by generation stage."
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
        help="Enable tracemalloc in addition to process RSS/private memory.",
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

            contract = build_api_contract(graph)
            del graph
            trace.snapshot("contract_built")

            adapter = resolve_language_adapter(args.language)
            template_root = resolve_template_root(
                adapter=adapter,
                templates_path=args.templates,
            )
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
            template_contract = replace(
                template_contract,
                emit=replace(
                    template_contract.emit,
                    meta={
                        **template_contract.emit.meta,
                        "jsonl_cache": str(jsonl.cache_dir),
                        "jsonl_reused": jsonl.reused,
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
                del emission

            del template_contract
            del contract
            del jsonl
            gc.collect()
            trace.snapshot("released")

            for snapshot in trace.snapshots:
                print(snapshot.summary())
            if args.json:
                print(
                    json.dumps(
                        [snapshot.to_json() for snapshot in trace.snapshots],
                        indent=2,
                        sort_keys=True,
                    )
                )
        finally:
            trace.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
