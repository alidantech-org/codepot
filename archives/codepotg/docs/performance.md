# CodepotG performance architecture

CodepotG separates durable source storage, lookup indexes, in-memory working sets,
and output writes so a large OpenAPI contract does not require one unbounded object
or one disk call per lookup.

## Storage tiers

### Raw source records: JSONL

The compiled cache keeps raw OpenAPI records in section files such as:

```text
paths.jsonl
components/schemas.jsonl
components/parameters.jsonl
x-codegen/resources.jsonl
x-codegen/entities.jsonl
```

Each line is addressable by byte offset and length. Templates and planners do not scan
these files. A raw line is read only when a selected record is explicitly loaded.

### Lookup and planning indexes: SQLite

`index.sqlite` stores:

- stable record locations;
- definitions by ref, key, and operation id;
- semantic mentions such as resource, kind, entity, and frontend;
- forward dependency facts used for reverse-dependency queries.

Selection planning queries SQLite for lightweight handles. Handle enumeration uses
bounded `fetchmany()` batches. JSONL remains the source of raw authored values, while
SQLite provides indexed lookup and filtering.

### Hot memory

Definitions, query results, lazy record proxies, and loaded raw records use bounded
byte-aware caches. Limits are derived from current available memory and the source size.
The runtime does not reserve all system memory and scales buffers down on constrained
hosts.

## Adaptive runtime tuning

CodepotG reads:

- logical CPU count;
- total physical memory when available;
- currently available physical memory;
- OpenAPI source size;
- planned output count.

It derives bounded values for:

- JSONL record queue depth and pending bytes;
- SQLite page cache;
- hot lookup caches;
- render workers;
- write workers;
- pending rendered files and bytes;
- write batch files and bytes.

The selected limits are reported as `Runtime tuning:` diagnostics.

Optional overrides:

```text
CODEPOTG_RENDER_WORKERS
CODEPOTG_WRITE_WORKERS
CODEPOTG_WRITE_BATCH_FILES
```

Use overrides only after measuring the adaptive defaults on the target machine.

## Rendering and writing

Jinja environments and compiled templates are reused for every output in one generation.
They are cleared after the generation completes, so the speed benefit does not become a
long-lived memory retention problem.

Rendered files enter a byte-bounded queue. The writer drains bounded batches and uses a
small worker pool. Every individual output still uses compare-before-write and atomic
replacement. A dependency is released only after its provider file completes.

Legacy folder packs and graph packs both use the adaptive queued runtime during normal
generation. The historical eager planning API remains available for callers that inspect
rendered plan content directly.

## Event and progress overhead

The durable event ledger records compiler start and completion by default. Per-record
events and callbacks are disabled because they add one serialization/write or callback
per OpenAPI record.

Detailed diagnostics can be enabled explicitly:

```text
CODEPOTG_JSONL_RECORD_EVENTS=1
CODEPOTG_JSONL_RECORD_PROGRESS=1
```

## YAML compatibility

JSON is the true streaming input. YAML requires one bounded compatibility parse and a
canonical JSON conversion. The converted source is persisted as:

```text
.codepotg/cache/<source>/source.json
```

Unchanged YAML reuses that conversion and the SQLite/JSONL cache. Prefer OpenAPI JSON for
the lowest cold-start time and peak memory.

## Profiling

Use process-memory and speed profiling without Python allocation tracing:

```bash
python scripts/profile_memory.py tests/fixtures/openapi.json --emit --json
python scripts/profile_memory.py tests/fixtures/openapi.yaml --emit --json
```

The report includes per-stage elapsed time, RSS, peak RSS, Windows private bytes, total
system memory, and available system memory.

`--full` enables ten-frame `tracemalloc` diagnostics. It is intentionally expensive and
must not be used as a production speed benchmark:

```bash
python scripts/profile_memory.py tests/fixtures/openapi.json --full --emit
```

## Interpreting release behavior

A high process peak is not by itself a leak. Compare `contract_built`,
`emission_complete`, and `released`:

- Python allocations dropping after `released` means object graphs were released.
- RSS remaining above the Python heap can be allocator or OS cache reuse.
- Repeated runs whose released private bytes stabilize are bounded.
- Repeated growth in released Python/private bytes requires a retention investigation.

## Headless selected documents

`build_selected_openapi_document()` is the guarded foundation for fully headless graph
planning. It:

1. enumerates selected handles through SQLite;
2. reads exact JSONL records only for those handles;
3. follows only reachable internal `$ref` dependencies;
4. preserves parent path metadata for selected operations;
5. reconstructs a reduced OpenAPI document for compatibility inference.

This path remains guarded until each bundled graph pack has output-parity tests. Normal
compatibility packs already skip unused normalized views and use the queued runtime.
