# CodepotG Package Readiness Tasks

Branch: `chatgpt/codepotx-restart`

This is the authoritative execution checklist for bringing `packages/python/codepotg` to a usable release state. It reconciles:

- `NORMALIZED_CONTRACT_TASKS.md`;
- `NORMALIZED_CONTRACT_VERIFICATION_TASKS.md`;
- `docs/`;
- `agents/tasks/24-codepotg-jsonl-lazy-generation.md`;
- the implemented JSONL, hot-index, queue, selection, and virtual-output work.

Status legend:

```text
[ ] pending
[-] active
[x] complete and evidenced
[!] blocked by an external or explicit product decision
```

## Release goal

CodepotG must compile OpenAPI through a JSON-first, indexed, memory-bounded pipeline; expose a lossless normalized contract through selection-specific lazy contexts; plan dependencies and output paths from an approved `paths.yaml` contract; render and write files incrementally; preserve existing packs through compatibility aliases; and pass package, fixture, CLI, documentation, build, and release validation.

## R0 — Baseline and task reconciliation

- [-] Record the current branch head and latest local validation evidence.
- [-] Reconcile completed JSONL work into Task 24.
- [ ] Reconcile verified normalized-contract work into both normalized task files.
- [ ] Inventory bundled template packs and current `paths.yaml` shapes.
- [ ] Inventory current stable and compatibility template variables.
- [ ] Link this checklist from package and task documentation.

Completion evidence:

```text
one current checklist
no completed work left falsely pending
no pending work marked complete without tests
```

## R1 — JSONL compiler and indexes

- [x] JSON-first streaming parser without `json.load()` in compilation.
- [x] Separate JSONL sections for paths, components, and supported `x-codegen` collections.
- [x] Same-byte hashing and deterministic section hashes.
- [x] Direct byte-offset and byte-length lookup.
- [x] Source hash reuse and atomic cache replacement.
- [x] Bounded hot index and disk-backed lookup.
- [x] Definition, mention, resource, kind, tag, operation, and dependency indexing.
- [x] Visible `codepotg jsonl` command and deterministic events.
- [ ] YAML compatibility adapter that emits a JSON-preferred warning.
- [ ] Index relation, access, frontend, generated-output, template, symbol, and import facts where present.
- [ ] Incremental section replacement by section hash rather than replacing the complete cache directory.
- [ ] JSONL cache schema/version migration diagnostics.

## R2 — Selection and virtual output planning

- [x] Canonical internal selections.
- [x] `each`, `all`, and per-resource grouping.
- [x] Shared raw-record loading across several emissions.
- [x] Bounded raw-context cache.
- [x] Portable planned/written virtual-output registry.
- [x] Duplicate output and unsafe-path validation.
- [ ] Connect template descriptors to canonical selections.
- [ ] Plan several emissions from one selected source through public generation.
- [ ] Add selection-specific planned context metadata.
- [ ] Let import lookup consume the virtual registry without rescanning templates or JSONL.

## R3 — Approved `paths.yaml` contract

The human design gate is approved. The implementation must remain additive and continue loading existing `folders` packs.

- [-] Add named `selections` separate from output emissions.
- [-] Add named `emissions` with template, selection, scope, alias, output, lifecycle, and provided-symbol facts.
- [ ] Add explicit dependency-provider declarations per emission.
- [ ] Add first-class barrel declarations and exported emission membership.
- [ ] Validate ids, aliases, selectors, scopes, templates, output paths, providers, and barrel references.
- [ ] Reject output collisions, provider ambiguity, cycles, and invalid transitive overlap.
- [ ] Preserve legacy `folders` behavior through an internal compatibility translation.
- [ ] Migrate bundled packs only after compatibility tests cover old and new shapes.
- [ ] Extend `codepotg paths` to show the resolved graph and migration diagnostics.

## R4 — Dependency graph, providers, imports, and barrels

- [ ] Calculate exact provided refs and symbols for every planned emission.
- [ ] Validate that a requested dependency is actually emitted by its configured provider.
- [ ] Expand barrel contents transitively.
- [ ] Reject overlapping providers only for the same required ref or symbol.
- [ ] Build a deterministic dependency DAG.
- [ ] Detect direct and transitive cycles.
- [ ] Schedule scoped barrels after all declared members are written.
- [ ] Register written barrels immediately and release dependants without replanning.
- [ ] Build language-neutral dependency facts and adapter-owned final import syntax.

## R5 — Lazy normalized context

- [ ] Replace full-contract template access in the new pipeline with bounded globals plus selected context.
- [ ] Add lazy ref, resource, operation, schema, entity, access, and frontend resolvers.
- [ ] Add render-local or bounded LRU resolver caches.
- [ ] Add cycle, depth, item-count, and byte-size limits.
- [ ] Preserve raw and extension escape hatches without exposing mutable source objects.
- [ ] Define and test context variables for every supported selection.
- [ ] Keep legacy global aliases available only through the compatibility pipeline until migrated.

## R6 — Incremental generation runtime

- [ ] Integrate JSONL compilation into `GeneratorApp.generate` and `GeneratorApp.emit`.
- [ ] Add bounded planner, resolver, renderer, generated-file writer, and event queues.
- [ ] Stream `selected`, `resolved`, `planned`, `rendered`, `queued`, `written`, `unchanged`, `refused`, `failed`, and `completed` events.
- [ ] Let generated files appear while later outputs are still being planned.
- [ ] Atomically write generated files.
- [ ] Propagate worker failures and cancel dependent work.
- [ ] Drain queues and verify all workers before success.
- [ ] Avoid retaining the complete normalized contract, complete plan, or all rendered content.
- [ ] Preserve dry-run, lifecycle, refusal, refresh, before-command, and after-command behavior.

## R7 — Lossless normalized contract

Complete the outstanding items from `NORMALIZED_CONTRACT_TASKS.md`, in this dependency order:

- [ ] shared presence, origin, reference, schema-use, collection, note, and diagnostic primitives;
- [ ] object-level raw and extension preservation;
- [ ] complete JSON Schema values, constraints, arrays, objects, composition, conditions, annotations, and dialect facts;
- [ ] document, server, security, path, parameter, request, media, response, callback, webhook, and operation facts;
- [ ] resource, operation-role, UI, target-schema, and source metadata;
- [ ] cache, access, runtime transport, and hooks;
- [ ] base entities, inheritance, fields, query capabilities, backend visibility, relations, constraints, and rules;
- [ ] schema roles and projections;
- [ ] frontends, components, screens, links, and selections;
- [ ] canonical root, contextual variables, classified collections, safe empty behavior, and complete debug output.

Every item must follow the verification rules in `NORMALIZED_CONTRACT_VERIFICATION_TASKS.md`.

## R8 — Packs and adapters

- [ ] Migrate TypeScript to normalized constraints, operations, imports, and lazy contexts.
- [ ] Migrate Next.js while preserving framework behavior.
- [ ] Migrate Dart while preserving null-safety and output compatibility.
- [ ] Make debug output the canonical completeness report.
- [ ] Verify a legacy project-owned pack.
- [ ] Verify a normalized project-owned pack.
- [ ] Build the universal adapter test kit before expanding adapter categories.
- [ ] Treat additional language families as post-core release work unless explicitly promoted to the core release gate.

## R9 — Documentation and author contract

- [ ] Rewrite the `paths.yaml` guide around the implemented syntax.
- [ ] Document every selection and grouping mode.
- [ ] Document every selection-specific context variable.
- [ ] Document bounded globals and compatibility globals separately.
- [ ] Document lazy resolvers and their JSONL-read behavior.
- [ ] Document providers, direct imports, barrels, conflict rules, cycles, and scheduling.
- [ ] Document old-to-new pack migration.
- [ ] Link the documentation index from the package README.
- [ ] Add broken-relative-link tests.
- [ ] Ensure documentation describes implemented behavior rather than unverified target behavior.

## R10 — Verification and release

- [ ] Focused unit and integration tests for every completed feature.
- [ ] Real TypeScript and Dart templates reading every applicable new variable.
- [ ] Real generation through `GeneratorApp.generate` and public CLI.
- [ ] Failure, missing-value, unresolved-reference, cycle, overlap, and unsafe-path tests.
- [ ] Large-fixture memory and lazy-load assertions.
- [ ] OpenAPI 3.0.3 and 3.1.0 equivalence tests.
- [ ] TypeScript, Next.js, Dart, debug, legacy custom-pack, and normalized custom-pack compatibility.
- [ ] Full pytest and Ruff.
- [ ] Build source distribution and wheel.
- [ ] Validate wheel contents and install into a clean environment.
- [ ] CLI startup and representative generation from the installed wheel.
- [ ] Documentation link validation.
- [ ] `lost values = 0` and `unresolved internal references = 0` on the shared real contract.
- [ ] Update every task file and close all implementation issues only after evidence is recorded.

## Working discipline

For each batch:

1. inspect affected source, contracts, templates, adapters, and tests;
2. add focused tests where practical;
3. make the smallest coherent additive change;
4. preserve compatibility aliases and old pack behavior;
5. run focused tests, complete tests, and Ruff;
6. generate representative files;
7. update this checklist and the source task file;
8. commit the batch to `chatgpt/codepotx-restart`;
9. continue immediately with the next unblocked batch.
