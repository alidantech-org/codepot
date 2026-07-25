# CodepotG Package Readiness Tasks

Branch: `chatgpt/codepotx-restart`

This is the authoritative implementation and release checklist for `packages/python/codepotg`. It consolidates:

- `NORMALIZED_CONTRACT_TASKS.md`;
- `NORMALIZED_CONTRACT_VERIFICATION_TASKS.md`;
- `docs/`;
- `agents/tasks/24-codepotg-jsonl-lazy-generation.md`.

Status legend:

```text
[ ] pending
[-] implemented, awaiting the next local validation gate
[x] complete and evidenced
[!] blocked by an external release/environment requirement
```

## Validated baseline

Validated at commit `18ac37322bb48e8021fa51ac7e81792be023c264`:

```text
8 focused tests passed
318 total tests passed
Ruff passed
```

## R0 — Baseline and task reconciliation

- [x] Create one current readiness checklist.
- [x] Record the current validated branch checkpoint.
- [x] Separate the supported CodepotG release set from the unbounded universal-adapter catalog.
- [-] Reconcile completed JSONL work into Task 24 after the current normalized-root gate.
- [-] Reconcile normalized-contract task files after focused/full validation.
- [ ] Inventory and migrate every bundled template pack.

## R1 — JSON-first compiler and indexed cache

- [x] Stream OpenAPI JSON without `json.load()` in compilation.
- [x] Validate root, OpenAPI version, and paths while streaming.
- [x] Extract direct raw records before normalization.
- [x] Write separate JSONL path, component, and supported `x-codegen` sections.
- [x] Hash the exact serialized line bytes.
- [x] Record direct byte offsets and lengths.
- [x] Keep `manifest.json` compact.
- [x] Reuse valid source-hash caches through atomic replacement.
- [x] Support YAML through a deterministic compatibility adapter.
- [x] Warn that JSON is the recommended bounded-memory input.
- [x] Expose visible `codepotg jsonl` output and compiler events.
- [x] Integrate cache compilation/reuse into normal generate and emit workflows.
- [ ] Add incremental per-section cache replacement instead of complete cache-directory replacement.
- [ ] Add explicit cache schema/version migration diagnostics.

## R2 — Headless indexes and bounded lazy lookup

- [x] Sharded definition indexes.
- [x] Sharded mention indexes.
- [x] Forward and reverse dependency indexes.
- [x] Ref, key, and operation-id aliases.
- [x] Resource, kind, tag, schema, DTO, enum, entity, and operation facts.
- [x] Access, frontend, screen, relation, template, import, and generated-file semantic mentions.
- [x] Exact operation pointers.
- [x] Bounded entry/byte hot indexes with eviction.
- [x] Direct-seek raw record loading from disk.
- [x] Lazy ref, key, operation, resource, mention, dependant, and chain resolvers.
- [x] Resolver byte, entry, record, depth, and related-item limits.
- [x] Reload evicted records from disk.

## R3 — Approved `paths.yaml` graph

- [x] Preserve legacy `folders` packs.
- [x] Add named `selections`.
- [x] Add explicit `emissions`.
- [x] Add first-class `barrels`.
- [x] Support `each`, `all`, and `resource` scopes.
- [x] Reuse one selection across several emissions.
- [x] Support `paths.yaml` and `paths.yml` with ambiguity checks.
- [x] Validate strict unknown keys, aliases, templates, paths, providers, and barrels.
- [x] Reject unsafe paths, output collisions, node collisions, and dependency cycles.
- [x] Expose the resolved author graph through `codepotg paths`.

## R4 — Providers, imports, barrels, and virtual outputs

- [x] Register virtual output paths before files exist.
- [x] Track source refs, selected refs, symbols, capabilities, templates, resources, and status.
- [x] Require explicit providers for importable dependencies.
- [x] Verify that configured providers emit the exact requested ref.
- [x] Support direct and barrel providers.
- [x] Expand barrel refs, symbols, and capabilities transitively.
- [x] Reject overlap only when providers can supply the same requested ref.
- [x] Support same-emission sibling providers.
- [x] Exclude same-file self dependencies from imports and scheduling.
- [x] Register outputs as written immediately.
- [x] Release dependants without rescanning JSONL or templates.

## R5 — Bounded progressive generation

- [x] Bounded compiler record and event queues.
- [x] Bounded graph render workers.
- [x] Byte- and file-bounded generated-write queue.
- [x] One disk writer owns generated writes.
- [x] Atomic changed-aware file writes.
- [x] Release dependants only after physical writes.
- [x] Progressive planned, rendering, rendered, queued, written, unchanged, skipped, and completed events.
- [x] Failure propagation and dependent-work cancellation.
- [x] Queue draining and worker verification.
- [x] Dry-run and immutable-file behavior.
- [x] Queue high-water diagnostics.

## R6 — Correct bounded template context

- [x] Bounded project, language, emission, and frontend globals.
- [x] Selected alias and selection metadata.
- [x] File and virtual output metadata.
- [x] Provider facts and provider outputs.
- [x] Lazy `source`, `sources`, and `resolve` variables.
- [x] Hide complete compatibility collections from graph rendering.
- [x] Keep compatibility collections internal to selection resolution.
- [x] Expose source-preserving API root as `normalized`.
- [x] Expose standard HTTP/security/domain root as `domains`.
- [-] Expose complete JSON Schema facts as `schema_contract`.
- [-] Expose resource/operation runtime metadata as `codegen_contract`.
- [-] Expose inherited persistence entities as `entity_contract`.
- [-] Expose authored frontends as `frontend_contract`.

## R7 — Lossless normalized contract

### Shared primitives

- [x] Presence-aware values and origins.
- [x] Reference kinds and resolution states.
- [x] Shared schema-use contract.
- [x] Deterministic collections and collision facts.
- [x] Structured notes.
- [x] Frozen source objects, extensions, diagnostics, and loss counts.
- [x] Complete object-level source registry for supported OpenAPI and `x-codegen` objects.

### JSON Schema

- [x] Existing source-preserving schema and field views.
- [-] Complete annotations and scalar values.
- [-] Complete numeric and string constraints.
- [-] Complete arrays, tuple items, contains, and unevaluated items.
- [-] Complete object boundaries, dependencies, and unevaluated properties.
- [-] Complete composition and conditional schemas.
- [-] `$defs`, IDs, anchors, dynamic refs, and dialects.
- [-] Discriminator, external docs, malformed boundaries, and diagnostics.
- [-] Real Jinja consumption through `schema_contract`.

### Standard OpenAPI and HTTP

- [x] Root metadata and servers.
- [x] Security schemes and requirements.
- [x] Path items and effective parameters.
- [x] Request bodies, media types, responses, headers, links, and callbacks.
- [x] Operation-level security overrides.
- [ ] Complete typed reusable component registries beyond source-object lookup.
- [ ] Complete typed webhooks.
- [ ] Complete reusable-ref edge cases for parameters, bodies, responses, headers, links, and callbacks.

### Resource and operation metadata

- [x] Existing compatibility resource and operation metadata.
- [-] Typed resource route, tags, UI, access policies, hooks, and linked collections.
- [-] Typed operation identity, authored/inferred role origin, tags, and UI inheritance.
- [-] Parameter/query/params/body/response schema targets.
- [-] Named sources and primary-source selection.
- [-] Cache read and invalidation policies.
- [-] Access uses.
- [-] Runtime inbound/outbound transport.
- [-] Ordered hook definitions and lifecycle uses.
- [-] Preserved unresolved targets and diagnostics.
- [-] Real Jinja consumption through `codegen_contract`.

### Persistence entities

- [x] Existing compatibility entities.
- [-] Base and concrete entity registries.
- [-] Deterministic inheritance and effective fields.
- [-] Override identity and origin.
- [-] Public, backend, storage, editable, readonly, and queryable views.
- [-] Query capabilities and preserved unknown operators.
- [-] Composite relations and lifecycle helpers.
- [-] Indexes, unique constraints, and recursive rule expressions.
- [-] Missing-target and inheritance-cycle diagnostics.
- [-] Real Jinja consumption through `entity_contract`.

### Frontends

- [x] Existing compatibility frontend objects.
- [-] Explicit authored-only frontend registry.
- [-] Folder mappings and full routes.
- [-] Components with props, schemas, operation uses, tags, notes, and source.
- [-] Screens with params/query/body/response, placement, uses, tags, and notes.
- [-] Deterministic linked operation and schema collections.
- [-] Preserved unresolved uses and diagnostics.
- [-] Real Jinja consumption through `frontend_contract`.

## R8 — Template-pack migration

- [ ] Migrate bundled debug pack to the paths graph.
- [ ] Migrate bundled TypeScript pack to the paths graph.
- [ ] Migrate bundled Next.js pack to the paths graph.
- [ ] Migrate bundled Dart pack to the paths graph.
- [ ] Preserve legacy outputs and snapshots during migration.
- [ ] Verify provider/barrel imports in TypeScript output.
- [ ] Verify provider/barrel imports in Dart output.
- [ ] Verify one source record feeding multiple bundled emissions.
- [ ] Verify resource-scoped barrels in a bundled/project fixture.

## R9 — Documentation

- [x] Paths graph guide.
- [x] Bounded normalized roots guide.
- [x] Documentation index.
- [x] Relative-link tests.
- [ ] Reconcile `template-variables.md` target claims with actual compatibility and graph roots.
- [ ] Reconcile `x-codegen-metadata.md` with current exact field names.
- [ ] Expand JSONL/cache/queue CLI examples in the package README.
- [ ] Document every supported selection and grouping mode.
- [ ] Document every resolver and limit.
- [ ] Document provider conflicts, cycle errors, and barrel timing with complete examples.
- [ ] Document bundled-pack migrations.
- [ ] Document diagnostics and safe empty values.

## R10 — Verification and release

- [x] Baseline focused/full/Ruff gate at 318 tests.
- [-] Focused schema/codegen/entity/frontend contract tests.
- [-] Real graph-generation tests for all bounded normalized roots.
- [-] Full suite and Ruff after the normalized-root batch.
- [ ] OpenAPI 3.0.3 and 3.1.0 release fixtures.
- [ ] JSON and YAML parity generation.
- [ ] Build source distribution and wheel.
- [ ] Validate wheel contents with Twine.
- [ ] Install the wheel in a clean environment.
- [ ] Verify installed `codepotg --help`, `jsonl`, `paths`, `generate`, and representative generation.
- [ ] Verify packaged YAML and YML template configurations.
- [ ] Verify zero lost values and zero unresolved internal refs on release fixtures.
- [ ] Verify every documented stable root exists.
- [ ] Record final release commands and results.

## R11 — Adapter expansion policy

The universal adapter catalog in `NORMALIZED_CONTRACT_TASKS.md` is not a blocker for the existing CodepotG release. An adapter is complete only when it has a real template pack, focused tests, and an emitted artifact fixture.

- [ ] Maintain TypeScript, Next.js, Dart, and debug as the supported release set.
- [ ] Track additional languages and formats as separate scoped features.
- [ ] Do not mark an adapter complete from enum registration alone.

## Immediate execution order

1. Validate the normalized schema/codegen/entity/frontend batch.
2. Fix all focused/full/Ruff failures.
3. Complete typed reusable components and webhooks.
4. Migrate debug and TypeScript packs.
5. Migrate Next.js and Dart packs.
6. Reconcile public documentation against generated behavior.
7. Run build, wheel, clean-install, and installed-CLI gates.
8. Mark this checklist complete only from recorded evidence.
