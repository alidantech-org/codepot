# Performance and memory tracing

CodepotG has two distinct memory paths:

- JSON input is streamed into the indexed JSONL cache.
- YAML input is a compatibility path. It must first be parsed, but its canonical JSON
  conversion is written incrementally and persisted as `.codepotg/cache/<name>/source.json`.
  An unchanged YAML source reuses that conversion without parsing YAML again.

## Profile one generation pipeline

Run from `packages/python/codepotg`:

```bash
python scripts/profile_memory.py tests/fixtures/openapi.json --full --json
python scripts/profile_memory.py tests/fixtures/openapi.yaml --full --json
python scripts/profile_memory.py tests/fixtures/openapi.json --full --emit --json
```

The profiler reports these stages:

| Stage | Meaning |
|---|---|
| `start` | Imported process baseline. |
| `jsonl_ready` | Indexed JSONL cache compiled or reused. |
| `document_loaded` | Compatibility OpenAPI object is in memory. |
| `graph_inferred` | Schema, operation, resource, and dependency graph is built. |
| `contract_built` | Compatibility and normalized contracts are built. |
| `template_contract_built` | Language adapter and template objects are planned. |
| `emission_complete` | Optional templates have rendered and written. |
| `released` | Large locals were deleted and `gc.collect()` completed. |

Metrics:

- `rss`: current process working set;
- `rss_peak`: operating-system high-water working set;
- `private`: private committed bytes on Windows, or data bytes where available;
- `python`: currently traced Python allocations when `--full` is enabled;
- `python_peak`: peak traced Python allocations.

`rss_peak` never decreases because it is a high-water value. Python and the operating
system allocator may also retain freed arenas for later reuse, so current RSS may not
return to the startup baseline. A likely retained-object problem is indicated when both
`python` and `private` remain close to their peak at `released`, or when repeated runs
continue increasing rather than stabilizing.

## Trace normal generation

Set an environment variable before a normal `codepotg generate` or application call:

```bash
CODEPOTG_MEMORY_TRACE=1 codepotg generate
CODEPOTG_MEMORY_TRACE=full codepotg generate
```

`1` records process memory with minimal overhead. `full` also enables `tracemalloc`,
which is more detailed but slower and should be used for diagnosis rather than routine
builds.

To save stage snapshots as JSON Lines:

```bash
CODEPOTG_MEMORY_TRACE=full \
CODEPOTG_MEMORY_TRACE_FILE=.codepotg/memory-trace.jsonl \
codepotg generate
```

Memory summaries are also included in generation diagnostics while tracing is enabled.

## Test fixture tiers

The suite deliberately separates fixtures:

- `tests/fixtures/openapi.json` is the canonical large streaming and real-contract fixture.
- `tests/fixtures/openapi.yaml` verifies equivalent YAML compatibility and parity.
- `tests/fixtures/project_openapi.yaml` is the focused fixture for exact TypeScript and
  Dart project-pack outputs.
- Tiny inline documents are limited to malformed, missing-reference, collision, and cycle
  unit tests.

This avoids compiling the same large specification once per language, format, assertion,
or project copy while preserving production-scale coverage.
