# OpenAPI source-adapter implementation plan

This package loads OpenAPI sources and normalizes them directly into the neutral CodepotG IR. It must not expose OpenAPI objects to target adapters/templates and must not duplicate source graphs for compatibility.

## OA-001 — Package and plugin foundation

**Status:** planned

**Dependencies:** core source-adapter port, neutral IR, plugin/version contracts

- [ ] Add isolated package metadata, src layout, typing marker, README, and tests.
- [ ] Register `openapi` in `codepotg.source_adapters`.
- [ ] Declare supported OpenAPI versions, plugin/core/IR compatibility, capabilities, and behavior version.
- [ ] Implement immutable adapter options and factory context.
- [ ] Add architecture tests proving no language, template engine, pack, writer, CLI, command, or old-generator imports.

## OA-002 — Typed option schema

**Status:** planned

Define typed options, descriptors, defaults, validation, examples, and introspection for:

- [ ] strict versus tolerant validation policy;
- [ ] external reference policy;
- [ ] authorized roots/hosts supplied by the host;
- [ ] operation ID policy;
- [ ] naming conflict policy at the semantic source level only;
- [ ] unsupported-feature diagnostic policy;
- [ ] source size/reference depth limits;
- [ ] extension preservation policy through bounded IR extensions.

Unknown options are errors. Options must not include target language choices.

## OA-003 — Controlled source loading

- [ ] Support local file and in-memory YAML/JSON inputs.
- [ ] Support external references only through a host-supplied controlled loader.
- [ ] Preserve exact source identity and spans.
- [ ] Enforce path containment, network authorization, size limits, cancellation, and credential redaction.
- [ ] Avoid reading the same document more than once per session/digest.

## OA-004 — Parse and structural validation

- [ ] Parse YAML/JSON safely with duplicate key detection.
- [ ] Validate OpenAPI version and root structure.
- [ ] Convert parser/library exceptions into typed diagnostics.
- [ ] Preserve source spans for paths, schemas, fields, operations, parameters, responses, and references.
- [ ] Avoid mutable global parser configuration.

## OA-005 — Reference resolver

- [ ] Build canonical document/reference identities.
- [ ] Resolve local and authorized external references once.
- [ ] Detect reference cycles, excessive depth, missing targets, and incompatible target kinds.
- [ ] Preserve original reference provenance.
- [ ] Memoize by canonical identity inside the operation/session, not a global map.

## OA-006 — Schema/type normalization

- [ ] Normalize primitive types, formats, arrays, objects, maps/additional properties, enums, composition, references, literals/defaults, required properties, nullable values, and read/write semantics into neutral IR.
- [ ] Preserve optional presence versus nullable value.
- [ ] Normalize constraints only when represented by approved IR types/extensions.
- [ ] Report ambiguous/unsupported constructs rather than targeting TypeScript/Dart directly.
- [ ] Ensure deterministic field/order identity.

## OA-007 — Operation normalization

- [ ] Normalize paths, methods, operation IDs, tags/resources, parameters, request bodies, media types, responses, headers, errors, security requirements, and deprecation metadata.
- [ ] Link semantic schema references by IR IDs.
- [ ] Handle missing operation IDs through typed source policy without target naming assumptions.
- [ ] Produce stable operation ordering.

## OA-008 — Provenance and bounded extensions

- [ ] Attach source spans and canonical source paths to IR nodes.
- [ ] Preserve approved OpenAPI extensions only as safe immutable scalar/structured values under namespaced keys.
- [ ] Prevent parser objects, raw mutable mappings, or resolver instances from entering IR.
- [ ] Add size/depth limits and serialization tests.

## OA-009 — Adapter facade and digest

- [ ] Compose loader, parser, resolver, validator, and normalizers behind the public source-adapter protocol.
- [ ] Produce immutable source result, diagnostics, IR, and source/behavior digest.
- [ ] Include all option and authorized-loader behavior in digest identity.
- [ ] Support cancellation between documents, references, schemas, and operations.

## OA-010 — Conformance and focused tests

- [ ] Pass shared source-adapter conformance.
- [ ] Add minimal OpenAPI 3.0/3.1 fixtures for every supported semantic construct.
- [ ] Add invalid reference, cycle, duplicate, unsupported, path escape, unauthorized network, and cancellation tests.
- [ ] Prove parse-once/reference-once behavior through instrumentation.
- [ ] Prove deterministic immutable IR.

## OA-011 — Realistic and performance fixtures

- [ ] Add a realistic large OpenAPI document used by official pack integrations.
- [ ] Benchmark parse, reference resolution, normalization, memory, and cancellation latency.
- [ ] Add regression thresholds appropriate to the repository environment.
- [ ] Avoid giant opaque snapshots; keep inspectable summaries and selected exact assertions.

## OA-012 — Documentation and release

- [ ] Document supported OpenAPI versions/features and diagnostics for unsupported/ambiguous behavior.
- [ ] Document local, memory, and controlled external reference policies.
- [ ] Build wheel/sdist and test independent installation/entry-point discovery.

## Completion gate

- shared source conformance passes;
- source is parsed and references resolved once per session;
- OpenAPI-specific types do not escape into core/adapters/templates;
- optional/nullable semantics remain accurate;
- unauthorized filesystem/network access is impossible through the adapter;
- output IR is deterministic, immutable, and directly canonical.
