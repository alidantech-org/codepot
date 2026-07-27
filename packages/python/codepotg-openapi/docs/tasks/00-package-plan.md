# OpenAPI source-adapter implementation plan

This package loads OpenAPI sources, decodes supported typed/versioned Codepot `x-codegen` metadata, and normalizes directly into the closed CodepotG kernel. It must not expose OpenAPI objects to target adapters/templates, duplicate source graphs for compatibility, or extend semantic objects, facets, selectors, or context contracts.

PR #29 merged a useful but incomplete foundation. The package is not a usable source adapter until OA-001, OA-017, and OA-018 are completed through the public entry point. See the audit and fix handoff before continuing.

## OA-001 — Package and plugin foundation

**Status:** fix required; metadata exists but the advertised entry-point factory imports missing `codepotg_openapi.adapter`

**Dependencies:** core source-adapter port, closed semantic kernel, plugin/version contracts

- [x] Add isolated package metadata, src layout, typing marker, README, and subsystem unit tests.
- [x] Register `openapi` in `codepotg.source_adapters` metadata.
- [x] Declare OpenAPI/plugin/core/IR compatibility and initial capabilities.
- [x] Implement immutable adapter options.
- [ ] Add the real `OpenApiSourceAdapter` production module and factory.
- [ ] Add import-smoke, entry-point, architecture, and isolated-distribution tests.
- [ ] Prove the descriptor cannot register semantic objects, facets, selectors, expression roots, or template-context properties.

## OA-002 — Typed option schema

**Status:** implemented foundation in PR #29

- [x] Strict versus tolerant validation policy.
- [x] External-reference policy.
- [x] Deterministic grouping and multi-tag policy.
- [x] Operation-ID policy.
- [x] `x-codegen` strictness policy placeholder.
- [x] Source size, reference depth, document count, and bounded preservation limits.
- [x] Unknown-option and wrong-value rejection.
- [ ] Integrate every option into the final adapter digest and behavior tests.

Options must not include target-language/framework choices, selectors, facets, or generated syntax rules.

## OA-003 — Controlled source loading

**Status:** partial; loading exists but cache/session isolation must be fixed

- [x] Support absolute local files and in-memory YAML/JSON inputs.
- [x] Support external documents only through local containment or a host-supplied controlled loader.
- [x] Preserve source identities.
- [x] Enforce path containment, network authority, source-size limits, cancellation, and credential redaction.
- [ ] Make reference caching explicitly normalization-session-owned rather than loader-instance-owned.
- [ ] Prove no stale document or host-loader result crosses two `normalize()` calls.
- [ ] Prove each canonical document is read once inside one session.

## OA-004 — Parse and structural validation

**Status:** partial; standard parser exists but YAML alias/depth/item hardening is required

- [x] Parse JSON/YAML with duplicate-key detection.
- [x] Validate OpenAPI version and root structure.
- [x] Convert ordinary parser/library failures into diagnostics.
- [x] Preserve YAML node spans and root JSON spans.
- [x] Avoid mutable global parser configuration.
- [ ] Detect recursive YAML aliases and active-node cycles.
- [ ] Add explicit YAML conversion depth, node/item, and alias-expansion limits.
- [ ] Convert `RecursionError` and limit violations into stable diagnostics.
- [ ] Locate and validate typed `x-codegen` roots only after OA-010 exists.

## OA-005 — Reference resolver

**Status:** implemented foundation; public-facade and session-isolation integration remain

- [x] Build canonical document/reference identities.
- [x] Resolve local and authorized external references.
- [x] Detect reference cycles, excessive depth, missing targets, and incompatible target kinds.
- [x] Preserve original reference provenance and safe reference text.
- [x] Memoize by canonical identity within one resolver.
- [x] Keep parsed source objects private to this package.
- [ ] Prove parse-once/reference-once through the final adapter facade.
- [ ] Ensure the loader cache cannot outlive the resolver/normalization session.

## OA-006 — Schema/type normalization

**Status:** substantial partial in PR #29

- [x] Normalize primitives, arrays, objects, maps, enums, composition, aliases/references, literals, required fields, nullable values, read-only facts, and known constraints into structural schemas.
- [x] Preserve optional presence versus nullable value where representable.
- [x] Produce deterministic schema/field identities and provenance.
- [x] Diagnose unsupported constructs instead of introducing target syntax.
- [x] Reject unsupported controlled schema roles rather than creating entity/model/request/response kinds.
- [ ] Complete exact OpenAPI 3.0/3.1 fixture coverage for formats, examples/defaults, read/write behavior, composition, recursive refs, and unsupported cases.
- [ ] Run final core validation through OA-017.
- [ ] Decode explicit approved schema roles only after OA-010 exists and the core contract supports them.

## OA-007 — Group normalization

**Status:** substantial partial in PR #29

- [x] Implement deterministic tag/explicit grouping helpers and fallback groups.
- [x] Keep groups as the neutral ownership root.
- [x] Link normalized schemas and operations to stable group ownership.
- [x] Avoid neutral resource/service/module/feature objects.
- [ ] Complete multi-tag and explicit `x-codegen` grouping fixtures through the public adapter.
- [ ] Verify tag provenance and duplicate ownership diagnostics end to end.

## OA-008 — Operation core and HTTP facet normalization

**Status:** substantial partial in PR #29 for the current public HTTP subset

- [x] Normalize stable operation IDs and deterministic fallbacks.
- [x] Normalize parameters and request bodies into neutral operation inputs.
- [x] Normalize successful responses and declared failures.
- [x] Link schema uses by semantic ID.
- [x] Create the current public HTTP method/path/operation-ID facet.
- [x] Keep HTTP facts out of the neutral operation core.
- [x] Produce deterministic operation ordering.
- [ ] Complete path/query/header/cookie/body/status/media/header bindings when the public `HttpFacet` exposes them.
- [ ] Normalize caused effects only through OA-010 typed metadata.
- [ ] Correct external referenced Path Item diagnostics to use the resolved document span.
- [ ] Add composed public-adapter fixtures.

## OA-009 — Security and access normalization

**Status:** not implemented

- [ ] Normalize supported security schemes into known policy mechanism facts.
- [ ] Preserve alternatives and conjunctive requirements.
- [ ] Normalize root/operation security into policy references and access facets.
- [ ] Resolve inherited access without inventing absent roles or conditions.
- [ ] Decode richer policies only through OA-010.
- [ ] Diagnose unresolved schemes and invalid overrides.

## OA-010 — Typed `x-codegen` decoder and stable IDs

**Status:** not implemented; README claims must remain corrected until this lands

- [ ] Define immutable typed decoders for every supported version.
- [ ] Validate version compatibility before semantic mapping.
- [ ] Preserve source spans and extension paths.
- [ ] Decode authored semantic IDs and relationships.
- [ ] Reject duplicate/conflicting IDs and references.
- [ ] Do not infer kernel concepts from unknown keys.
- [ ] Include typed metadata behavior in the digest.

## OA-011 — Storage mapping normalization

**Status:** not implemented

- [ ] Normalize typed persistence metadata into `group.storage.mappings`.
- [ ] Link mappings and fields to known schemas.
- [ ] Normalize stores, mapped fields, keys, indexes, relations, and constraints using known kernel types.
- [ ] Validate every source field and relation target.
- [ ] Do not create entity/model/repository/ORM objects.

## OA-012 — View and interaction normalization

**Status:** not implemented

- [ ] Normalize typed interaction metadata into views, parts, triggers, flows, and known access facts.
- [ ] Link triggers to operations by semantic ID.
- [ ] Validate ownership, IDs, references, and transitions.
- [ ] Do not create frontend/page/screen/component/widget roots.

## OA-013 — Events, listeners, and delivery normalization

**Status:** not implemented

- [ ] Normalize events with payload/context schema references.
- [ ] Normalize caused occurrences into effects.
- [ ] Normalize known publication/consumption/channel facts into the events facet.
- [ ] Normalize listeners as operations with trigger facets.
- [ ] Validate all event, channel, operation, and schema references.

## OA-014 — Execution hook normalization

**Status:** not implemented

- [ ] Normalize before, around, after-success, after-failure, and after-complete hooks.
- [ ] Reference ordinary operations with order, condition, binding, stop, and failure facts.
- [ ] Validate phases, ordering, mappings, and cycles.
- [ ] Do not create an arbitrary executable hierarchy.

## OA-015 — Workflow and compensation normalization

**Status:** not implemented

- [ ] Normalize workflows, inputs, outputs, failures, effects, and known facets.
- [ ] Normalize operation, decision, parallel, wait, and end steps.
- [ ] Link transitions and forward operations.
- [ ] Normalize optional compensation facts.
- [ ] Validate branches, waits, events, mappings, references, and reachability.
- [ ] Do not generate runtime-orchestrator syntax.

## OA-016 — Provenance and bounded extensions/raw

**Status:** partial in PR #29

- [x] Attach source identity and available spans to many parsed/normalized values.
- [x] Keep parser, resolver, mappings, library classes, and callables outside IR.
- [x] Add initial bounded preservation options and helpers.
- [ ] Complete key/type/depth/item/size enforcement across every preserved value.
- [ ] Add serialization and no-semantic-extension tests.
- [ ] Preserve typed `x-codegen` provenance after OA-010.

## OA-017 — Adapter facade and digest

**Status:** not implemented; critical blocker

- [ ] Add `src/codepotg_openapi/adapter.py` implementing the public source-adapter protocol.
- [ ] Compose options, loader, parser, resolver, typed metadata decoder, normalizers, diagnostics, and one session boundary.
- [ ] Construct one immutable `Contract`.
- [ ] Run `codepotg.ir.validate_contract`.
- [ ] Return `SourceAdapterResult` with deterministic diagnostics and digest.
- [ ] Include every behavior-affecting option/version/authority value in digest identity.
- [ ] Support cancellation across the composed pipeline.

## OA-018 — Conformance and focused tests

**Status:** not implemented at package/public-facade level; critical blocker

- [ ] Pass shared source-adapter conformance.
- [ ] Add import-smoke and entry-point invocation tests.
- [ ] Add architecture and negative ownership tests.
- [ ] Add OpenAPI 3.0/3.1 public-facade fixtures.
- [ ] Add invalid reference, cycle, duplicate, unsupported, path-escape, unauthorized-network, YAML-alias, and cancellation tests.
- [ ] Prove session isolation and parse/reference-once behavior.
- [ ] Prove deterministic immutable kernel output and diagnostics.
- [ ] Add wheel/sdist and isolated-install tests.

## OA-019 — Connected realistic and performance fixtures

**Status:** not implemented

- [ ] Add an inspectable realistic source with real typed metadata after OA-010..OA-015.
- [ ] Assert selected exact semantic relationships.
- [ ] Integrate with official packs only after those public contracts exist.
- [ ] Benchmark parse, resolution, decoding, normalization, validation, memory, and cancellation.
- [ ] Avoid giant opaque snapshots.

## OA-020 — Documentation and release

**Status:** not implemented; current README must remain truthful to foundation support

- [ ] Document actual supported standard OpenAPI features.
- [ ] Document typed `x-codegen` only after OA-010 passes.
- [ ] Document grouping, operation IDs, authority, diagnostics, and blockers.
- [ ] Add support and benchmark documents only with corresponding implementation.
- [ ] Build wheel/sdist and test independent installation and entry-point invocation.
- [ ] Run Ruff, format, complete tests, real-core compatibility, and clean-tree checks.

## Audit follow-up

See:

- [`../audits/2026-07-27-pr-29-audit.md`](../audits/2026-07-27-pr-29-audit.md)
- [`AUDIT_FIXES.md`](AUDIT_FIXES.md)

## Completion gate

The package is complete only when:

- the installed entry point returns a working `SourceAdapter`;
- shared source conformance passes;
- source and references are processed once per normalization session with no cross-session cache leakage;
- YAML aliases, depth, and expansion are bounded safely;
- typed/versioned `x-codegen` maps only into known kernel contracts;
- groups replace neutral resource assumptions;
- schemas remain structural and operation direction remains on schema uses;
- operations, storage, views, access, events/listeners, hooks, workflows, and compensation relationships are validated;
- OpenAPI-specific objects do not escape into IR or templates;
- unauthorized filesystem/network access is impossible;
- output IR is deterministic, immutable, source-provenanced, and core-valid;
- Ruff, format, full tests, build, isolated wheel installation, and clean-tree checks pass and are recorded.
