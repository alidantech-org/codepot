---
title: Performance, JSONL, and memory tracing
description: Understand streamed JSON input, cached YAML conversion, profiling stages, metrics, and diagnostic tracing.
product: codepotg
package: codepotg
order: 17
---

# Performance, JSONL, and memory tracing

CodepotG has separate input paths for JSON and YAML.

## JSON input

JSON is streamed into an indexed JSONL cache. Later stages can retrieve source records lazily rather than holding multiple complete decoded copies.

The cache is visible under `.codepotg/cache` so reuse and invalidation can be inspected.

## YAML input

YAML must first be parsed. CodepotG writes a canonical JSON conversion incrementally and persists it as:

```text
.codepotg/cache/<source>/source.json
```

An unchanged YAML file reuses that conversion without parsing YAML again.

For very large contracts, JSON is the preferred source format.

## Build or inspect JSONL

```bash
codepotg jsonl --help
```

Use the JSONL command to compile a visible indexed cache and inspect source-index behavior independently from full generation.

## Profile a pipeline

From `packages/python/codepotg`:

```bash
python scripts/profile_memory.py tests/fixtures/openapi.json --full --json
python scripts/profile_memory.py tests/fixtures/openapi.yaml --full --json
python scripts/profile_memory.py tests/fixtures/openapi.json --full --emit --json
```

## Profile stages

| Stage | Meaning |
|---|---|
| `start` | Imported process baseline |
| `jsonl_ready` | Indexed cache compiled or reused |
| `document_loaded` | Compatibility OpenAPI object is in memory |
| `graph_inferred` | Schema, operation, resource, and dependency graph built |
| `contract_built` | Compatibility and normalized contracts built |
| `template_contract_built` | Language adapter and template plan built |
| `emission_complete` | Optional templates rendered and written |
| `released` | Large locals released and garbage collection completed |

## Metrics

| Metric | Meaning |
|---|---|
| `rss` | Current process working set |
| `rss_peak` | Operating-system high-water working set |
| `private` | Private committed/data bytes where available |
| `python` | Current traced Python allocations |
| `python_peak` | Peak traced Python allocations |

`rss_peak` never decreases. Python and the system allocator may retain freed arenas, so current RSS does not always return to startup levels.

A likely retained-object issue is indicated when both traced Python memory and private memory remain near their peaks after `released`, or repeated runs continue growing instead of stabilizing.

## Trace normal generation

```bash
CODEPOTG_MEMORY_TRACE=1 codepotg generate sdk
CODEPOTG_MEMORY_TRACE=full codepotg generate sdk
```

- `1` records process metrics with lower overhead.
- `full` enables `tracemalloc` and should be used for diagnosis.

Write JSONL snapshots:

```bash
CODEPOTG_MEMORY_TRACE=full \
CODEPOTG_MEMORY_TRACE_FILE=.codepotg/memory-trace.jsonl \
codepotg generate sdk
```

Memory summaries are included in diagnostics while tracing is enabled.

## Template performance

- Prefer graph selections over repeated global scans.
- Declare providers and dependencies explicitly.
- Avoid copying `api.raw` into derived contexts.
- Use grouped emissions for intentional aggregation.
- Keep barrel planning based on emission facts, not filesystem scans.
- Avoid quadratic Jinja loops over large global collections.

## Cache behavior

Use `--refresh` for project cleanup, not as a general source-cache invalidation flag. Source caches use content and metadata checks and should be reused when inputs are unchanged.

## Fixture strategy

The package test suite separates production-scale streaming fixtures from small targeted unit fixtures. Custom pack tests should follow the same principle: one representative full contract plus focused edge cases.