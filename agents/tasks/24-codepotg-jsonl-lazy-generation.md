# Task 24 — CodepotG JSONL-first lazy generation architecture

Status: [ ]
Issue: open when the JSONL implementation is ready to begin
Depends on: CodepotG 1.0 baseline and current template/generation behavior remain passing
Commit: pending
Validation: pending

## Goal

Replace full-document, full-plan, and full-render generation with a JSON-first, memory-bounded pipeline that streams OpenAPI into indexed JSONL records, resolves template context lazily, plans imports from explicit template dependencies, and writes files incrementally through bounded queues.

The user must be able to see generated files appear progressively while later selections and files are still being planned and rendered. The full OpenAPI document, full normalized contract, complete rendered project, and unbounded work queues must never be required in memory at the same time.

## Non-goals

- Do not redesign `paths.yaml` without human approval.
- Do not normalize the entire OpenAPI document before JSONL extraction.
- Do not assume every DTO, enum, entity, schema, resource, or operation is emitted.
- Do not infer dependency providers when the template pack has not declared them.
- Do not require generated files to exist before output paths and imports can be planned.
- Do not place large ref, resource, dependency, or symbol indexes inside `manifest.json`.

## Architectural sequence

```text
OpenAPI JSON stream
  -> raw JSONL extraction
  -> headless indexes
  -> bounded hot index registry
  -> template selection
  -> lazy context resolution
  -> virtual output and dependency graph
  -> incremental render queue
  -> incremental write queue
  -> written-file registry
  -> event/log queue
```

YAML remains supported as a compatibility input, but CodepotG must warn that JSON is preferred for faster streaming, lower peak memory, and more predictable results.

## Phase 1 — JSONL compilation foundation

This is the first implementation change. Later planning work must not begin until this gate is stable.

### Input and streaming

- [ ] Add JSON-first OpenAPI loading through a true streaming parser.
- [ ] Ensure normal JSON compilation does not call `json.load()` or create the full OpenAPI object.
- [ ] Support YAML through a separate compatibility adapter.
- [ ] Emit a clear non-blocking warning recommending JSON when YAML is used.
- [ ] Apply limits to bounded root metadata such as `info`, `security`, and `servers`.

### Raw JSONL layout

- [ ] Write bounded root metadata and cache metadata to `manifest.json`.
- [ ] Write one direct OpenAPI path entry per line to `paths.jsonl`.
- [ ] Write each direct `components.*` collection to its own JSONL file.
- [ ] Write each supported direct `x-codegen.*` collection to its own JSONL file.
- [ ] Preserve the raw selected item without dependency resolution or full normalization.
- [ ] Store normalized POSIX cache paths regardless of host operating system.

Expected shape:

```text
.codepotg/cache/
  manifest.json
  paths.jsonl
  components/
    schemas.jsonl
    parameters.jsonl
    requestBodies.jsonl
    responses.jsonl
    securitySchemes.jsonl
  x-codegen/
    resources.jsonl
    frontends.jsonl
    access.jsonl
    baseEntities.jsonl
    entities.jsonl
  indexes/
  events.jsonl
```

### Hashing and direct lookup

- [ ] Serialize each line once and reuse the same bytes for hashing and writing.
- [ ] Store a deterministic per-line hash.
- [ ] Compute section hashes incrementally while lines are written.
- [ ] Record byte offset and byte length for direct `seek()` lookup.
- [ ] Write to temporary section files and atomically retain or replace them after hash comparison.
- [ ] Keep source-file byte hashing as a fast unchanged-input shortcut.

## Phase 2 — Headless indexing and registries

Indexing must classify and register small facts without building normalized contracts.

### Definition and mention indexes

- [ ] Assign every line a stable key and canonical ref when applicable.
- [ ] Index every definition by key, ref, kind, source file, offset, length, and hash.
- [ ] Index every meaningful mention of a ref, resource, schema, entity, operation, frontend, access rule, relation, tag, template, generated file, and import.
- [ ] Distinguish definition facts from usage/mention facts.
- [ ] Allow a relationship to be registered before its target definition appears.

Example facts:

```jsonl
{"index":"resource","value":"users","item":"operation:get:/users"}
{"index":"ref","value":"#/components/schemas/User","item":"operation:get:/users","purpose":"response"}
{"from":"schema:User","to":"schema:UserStatus","type":"ref"}
```

### Resource and dependency registries

- [ ] Register everything that declares, belongs to, or mentions a resource.
- [ ] Build a resource registry that can discover its paths, operations, schemas, DTOs, enums, entities, access rules, frontends, and generated outputs.
- [ ] Build forward and reverse dependency indexes from direct mentions.
- [ ] Keep registration append-only during extraction; consolidate only when a query shape requires grouping.

### Bounded in-memory indexes

- [ ] Keep hot ref, key, resource, dependency, and output-location indexes in memory.
- [ ] Enforce entry-count and estimated-byte limits.
- [ ] Use bounded LRU or sharded eviction rather than unlimited dictionaries.
- [ ] Treat disk indexes as the source of truth and reload evicted shards lazily.
- [ ] Never load raw JSONL records into the hot index registry.

## Phase 3 — Queue-based compiler and visible incremental output

### Bounded stage queues

- [ ] Separate reader, parser, index, planner, resolver, renderer, writer, and event/log stages.
- [ ] Use bounded queues so slow parsing, rendering, disk, or logs apply backpressure.
- [ ] Prevent large blobs from allowing unlimited new render/write work into memory.
- [ ] Define cancellation and error propagation across all stages.
- [ ] Drain queues and verify writer errors before reporting task success.

Conceptual flow:

```text
reader -> parser -> indexers -> planner -> resolver -> renderer -> file writer
                                  |                    |
                                  +------ events -------+-> log writer
```

### Concurrency ownership

- [ ] Use asynchronous or threaded workers for I/O-bound reads, lookups, file writes, and event writes.
- [ ] Use limited worker pools for CPU-bound parsing, hashing, context construction, and rendering.
- [ ] Give each JSONL/index stream one ordered writer owner so offsets and line integrity remain correct.
- [ ] Write generated files atomically through writer workers.
- [ ] Continue selecting, planning, and rendering while previous files wait in the write queue.

## Phase 4 — Selection model and lazy template planning

Selections define what source data is requested. Emissions define how selected data becomes generated output. One source record may feed several emissions without being loaded repeatedly.

### Known selection classes

The planner must expose typed, documented selection classes, including at least:

- schemas;
- primitives;
- DTOs;
- enums;
- entities;
- operations;
- paths;
- resources;
- access definitions;
- frontends;
- components and other supported OpenAPI/x-codegen collections.

### Selection scopes

- [ ] Support one selected item per output file.
- [ ] Support all selected items in one output file.
- [ ] Support all selected items for one resource in one output file.
- [ ] Support grouped selections such as all DTOs, enums, schemas, operations, or entities for one resource.
- [ ] Validate duplicate or ambiguous canonical selections.
- [ ] Load one underlying source record once, then plan all applicable emissions from it.

Example requirement:

```text
schema:CreateUserDto
  -> TypeScript type emission
  -> Zod schema emission
```

The JSONL record and lazy schema context are loaded once; each emission has its own template, output path, imports, and rendered result.

### Virtual output registry

- [ ] Evaluate templated output paths before physical files exist.
- [ ] Store normalized POSIX virtual paths.
- [ ] Register planned and written outputs by source ref, selection, emission/template, provided symbols, path, and status.
- [ ] Let import resolution use this registry without rescanning templates or JSONL files.

Example registry fact:

```json
{
  "ref": "#/components/schemas/CreateUserDto",
  "selection": "dtos",
  "emission": "dto-types",
  "file": "models/create_user_dto.ts",
  "status": "written"
}
```

## Phase 5 — `paths.yaml` direction approval gate

**Stop here for human approval before finalizing or implementing the new `paths.yaml` contract.**

Before approval, Codepot may:

- inventory current `paths.yaml` behavior;
- document selection and dependency requirements;
- prepare two or more concrete syntax directions;
- show validation implications and migration costs;
- identify backward-compatibility constraints.

Before approval, Codepot must not:

- choose final field names;
- redefine template identity semantics;
- lock selection/emission syntax;
- implement barrel dependency syntax;
- rewrite bundled template packs to an unapproved format.

The approval proposal must resolve:

1. canonical selection identity versus multiple emissions from one selection;
2. one-item, all-items, and per-resource grouping syntax;
3. explicit dependency-provider syntax;
4. direct-file versus barrel import syntax;
5. barrel export membership syntax;
6. template ordering and dependency graph declarations;
7. backward migration from existing `paths.yaml` packs.

## Phase 6 — Explicit dependency providers and barrel semantics

Begin only after the `paths.yaml` direction is approved.

### Explicit dependency providers

- [ ] Require each dependent emission to declare where DTOs, enums, entities, schemas, resources, operations, and other concepts are imported from.
- [ ] Validate that the selected provider actually emits the requested concept and includes the requested item.
- [ ] Refuse dependencies on templates whose selection cannot provide the requested item.
- [ ] Do not assume a DTO, enum, entity, or schema exists merely because it exists in OpenAPI.

### Effective provider conflict validation

- [ ] Expand each dependency provider to its effective provided symbol/selection set.
- [ ] Expand barrels transitively through their exported emissions.
- [ ] Reject overlapping providers only when two configured sources can provide the same required item or symbol.

Example invalid configuration:

```text
models-barrel provides DTOs + enums + entities
operation imports enums from models-barrel
operation imports DTOs directly from dto-types
```

The conflict is verifiable because `models-barrel` also provides DTOs, giving the operation two providers for the same DTO dependency.

A barrel containing only enums plus a direct DTO provider is valid because the effective sets do not overlap.

### Dynamic barrel scheduling

- [ ] Treat barrels as first-class template/emission nodes.
- [ ] Let a barrel explicitly export selected emissions/templates.
- [ ] Emit a barrel only after every output it exports is planned and successfully written.
- [ ] Register the written barrel immediately in the in-memory written-file registry.
- [ ] Release dependants of the barrel without recomputing its members, path, or provided symbols.

Scheduling must be a dynamic DAG, not a fixed “all barrels last” rule.

```text
dto-types ----+
               +-> models-barrel -> operations
enum-types ---+
```

## Phase 7 — Correct lazy context per template

### Context boundaries

Every template receives only:

- bounded global variables;
- file/output metadata;
- the context for its declared selection;
- declared dependency-provider facts;
- lazy resolvers for permitted related data.

It must not receive the complete OpenAPI contract.

### Selection-specific context

- [ ] Define the complete context contract for every supported selection.
- [ ] Give schema templates the complete selected schema context, including primitives, fields, arrays, constraints, composition, and direct refs.
- [ ] Let operations lazily request request bodies, parameters, responses, schemas, security, and resource facts.
- [ ] Let resources lazily request their registered operations, schemas, DTOs, enums, entities, access, frontends, and relations.
- [ ] Resolve related data through indexed JSONL byte lookups only when accessed or explicitly requested.
- [ ] Bound resolver caches to the current render or a small LRU.
- [ ] Detect resolver cycles and depth/size limit violations.

### Import planning

- [ ] Construct imports from explicit dependency providers and the virtual/written output registry.
- [ ] Collect per-file import facts while context is resolved and rendered.
- [ ] Avoid full-project import recomputation.
- [ ] Preserve language-neutral dependency facts and use injected language adapters for final syntax.

## Phase 8 — Incremental scheduling and logical dependency order

- [ ] Plan related emissions together when they share one selected source record.
- [ ] Render and queue leaf files as soon as their dependency paths and providers are known.
- [ ] Allow the writer to work while later templates and records are still being planned.
- [ ] Use graph readiness rather than a mandatory global plan barrier.
- [ ] Provide a default logical ordering where useful—primitives, enums, entities, DTOs/schemas, operations, resources, frontends—but let explicit graph edges determine actual readiness.
- [ ] Keep aggregate outputs blocked only until their declared members are written.
- [ ] Stream progress events for selected, resolved, planned, rendered, queued, written, unchanged, refused, failed, and completed states.

## Phase 9 — Documentation and template-author contract

Documentation is updated after the approved configuration and runtime behavior are implemented.

- [ ] Rewrite the `paths.yaml` guide around the approved syntax.
- [ ] Document every supported selection and grouping mode.
- [ ] Document every selection-specific variable and nested context shape.
- [ ] Document bounded global variables separately from selected-item variables.
- [ ] Document lazy resolver variables and when they trigger JSONL reads.
- [ ] Document explicit dependency providers and validation failures.
- [ ] Document direct imports, barrels, effective provider conflicts, and dynamic barrel timing.
- [ ] Document virtual output paths, normalized paths, and written-file registry facts.
- [ ] Provide complete template-pack examples for TypeScript and at least one second language.
- [ ] Update template-variable CLI/introspection output from the same typed contracts used by validation.
- [ ] Clearly mark JSON as the preferred input and explain the YAML compatibility tradeoff.

Primary documentation targets include:

```text
docs/paths-yaml.md
docs/template-packs.md
docs/template-variables.md
docs/generation.md
docs/architecture.md
packages/python/codepotg/README.md
```

## Validation and acceptance criteria

- [ ] A large JSON OpenAPI fixture compiles without constructing the full document.
- [ ] Peak memory remains bounded by configured queues, hot indexes, the largest active record, and bounded resolver caches.
- [ ] Per-line hashes, section hashes, offsets, and lengths are deterministic.
- [ ] Indexed lookups seek directly to one JSONL record without loading the complete JSONL file.
- [ ] Resource and ref indexes include definitions and all direct mentions.
- [ ] Files appear progressively while planning/rendering continues.
- [ ] Queue saturation applies backpressure rather than unbounded memory growth.
- [ ] One source record can drive several emissions without repeated full parsing.
- [ ] Provider validation rejects missing, incompatible, ambiguous, and transitively overlapping sources.
- [ ] Barrels emit immediately after their exported outputs are written and before their dependants.
- [ ] Import paths remain deterministic across Windows, Linux, and macOS.
- [ ] Writer and logger failures propagate before final success.
- [ ] Existing CodepotG tests remain passing or have explicit approved migrations.
- [ ] New memory, concurrency, deterministic-output, lazy-resolution, and migration tests pass.

## Preserved safety rules

- Generated files are atomic.
- Bounded queues provide backpressure.
- Success is reported only after required writers drain and failures are checked.
- Managed and immutable lifecycle rules remain enforced.
- Stale cleanup uses recorded managed outputs, not broad deletion.
- Dry-run performs no file, command, cache-commit, or cleanup mutation.
- Deterministic inputs produce deterministic JSONL records, indexes, plans, registry facts, and output bytes.
