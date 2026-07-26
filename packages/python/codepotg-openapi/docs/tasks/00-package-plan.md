# OpenAPI source-adapter implementation plan

This package loads OpenAPI sources, decodes supported typed/versioned Codepot `x-codegen` metadata, and normalizes directly into the closed CodepotG kernel. It must not expose OpenAPI objects to target adapters/templates, duplicate source graphs for compatibility, or extend semantic objects/facets/selectors/context contracts.

## OA-001 — Package and plugin foundation

**Status:** planned

**Dependencies:** core source-adapter port, closed semantic kernel, plugin/version contracts

- [ ] Add isolated package metadata, src layout, typing marker, README, and tests.
- [ ] Register `openapi` in `codepotg.source_adapters`.
- [ ] Declare supported OpenAPI versions, `x-codegen` schema versions, plugin/core/IR compatibility, capabilities, and behavior version.
- [ ] Implement immutable adapter options and factory context.
- [ ] Add architecture tests proving no language, template engine, pack, writer, CLI, command, old-generator, or private semantic-builder imports.
- [ ] Add tests proving the descriptor cannot register semantic objects, facets, selectors, expression roots, or template-context properties.

## OA-002 — Typed option schema

**Status:** planned

Define typed options, descriptors, defaults, validation, examples, and introspection for:

- [ ] strict versus tolerant OpenAPI validation policy;
- [ ] external reference policy;
- [ ] authorized roots/hosts supplied by the host;
- [ ] deterministic group/tag policy;
- [ ] operation ID policy;
- [ ] semantic naming conflict policy only;
- [ ] supported/required `x-codegen` version and strictness policy;
- [ ] unsupported-feature diagnostic policy;
- [ ] source size/reference depth limits;
- [ ] bounded unknown-extension preservation policy.

Unknown options are errors. Options must not include target language/framework choices, selectors, facets, or generated syntax rules.

## OA-003 — Controlled source loading

- [ ] Support local file and in-memory YAML/JSON inputs.
- [ ] Support external references only through a host-supplied controlled loader.
- [ ] Preserve exact source identity and spans.
- [ ] Enforce path containment, network authorization, size limits, cancellation, and credential redaction.
- [ ] Avoid reading the same canonical document more than once per session/digest.

## OA-004 — Parse and structural validation

- [ ] Parse YAML/JSON safely with duplicate-key detection.
- [ ] Validate OpenAPI version and root structure.
- [ ] Locate and structurally validate `x-codegen` roots before semantic decoding.
- [ ] Convert parser/library exceptions into typed diagnostics.
- [ ] Preserve spans for groups/tags, schemas, fields, operations, parameters, request bodies, responses, security, extensions, and references.
- [ ] Avoid mutable global parser configuration.

## OA-005 — Reference resolver

- [ ] Build canonical document/reference identities.
- [ ] Resolve local and authorized external references once.
- [ ] Detect reference cycles, excessive depth, missing targets, and incompatible target kinds.
- [ ] Preserve original reference provenance.
- [ ] Memoize by canonical identity inside the operation/session, not a global map.
- [ ] Keep resolved parser/source objects inside this package.

## OA-006 — Schema/type normalization

- [ ] Normalize primitives, formats, arrays, objects, maps/additional properties, enums, composition, references/aliases, literals/defaults, required properties, nullable values, read/write semantics, examples, and known constraints into structural kernel schemas.
- [ ] Preserve optional presence versus nullable value.
- [ ] Produce schema-use-compatible identities without assigning permanent input/output direction to schemas.
- [ ] Decode only approved controlled schema roles such as explicit `dto` where supplied by typed `x-codegen` metadata.
- [ ] Reject or diagnose attempts to normalize `model`, `entity`, request/response, class/interface/type/struct/record as schema kinds.
- [ ] Report ambiguous/unsupported constructs rather than targeting TypeScript/Dart/frameworks.
- [ ] Ensure deterministic schema/field/order identity and source provenance.

## OA-007 — Group normalization

- [ ] Implement one explicit behavior-versioned grouping policy for OpenAPI operations.
- [ ] Normalize tags/paths/typed `x-codegen` grouping into `contract.groups` without creating neutral resources/services/modules/features.
- [ ] Define deterministic fallback groups for untagged operations.
- [ ] Define behavior for operations with several tags without silently cloning semantic identity.
- [ ] Link schemas, operations, and typed `x-codegen` concepts to stable group ownership.
- [ ] Preserve source tag metadata through provenance/extensions where it is not the normalized group identity.

## OA-008 — Operation core and HTTP facet normalization

- [ ] Normalize operation IDs and stable semantic IDs.
- [ ] Normalize parameters and request bodies into neutral `operation.inputs` schema-use records.
- [ ] Normalize successful responses into `operation.outputs`.
- [ ] Normalize declared error responses into `operation.failures`.
- [ ] Normalize caused occurrences into `operation.effects` only when declared by known typed metadata.
- [ ] Normalize methods, paths, parameter locations, body/media types, status codes, response media/headers, and deprecation into `operation.facets.http`.
- [ ] Link every schema use by kernel semantic ID.
- [ ] Keep HTTP details out of neutral input/output/failure core fields.
- [ ] Handle missing operation IDs through typed source policy without target naming assumptions.
- [ ] Produce stable group/operation ordering.

## OA-009 — Security and access normalization

- [ ] Normalize supported OpenAPI security schemes into known policy mechanism facts.
- [ ] Preserve OpenAPI security requirement alternatives and conjunctive scheme requirements accurately.
- [ ] Normalize operation/root security requirements into declared access facet values and policy references.
- [ ] Resolve effective inherited access facts without inventing roles, permissions, ownership, or conditions absent from the source.
- [ ] Decode richer policies/roles/permissions/scopes/conditions only through typed/versioned `x-codegen` schemas.
- [ ] Diagnose unresolved schemes/policies and invalid overrides.

## OA-010 — Typed `x-codegen` decoder and stable IDs

- [ ] Define immutable typed decoders for every supported `x-codegen` version.
- [ ] Validate version compatibility before mapping any semantic value.
- [ ] Preserve source spans and original extension paths for every decoded value.
- [ ] Decode authored stable semantic IDs and explicit relationships.
- [ ] Reject duplicate/conflicting IDs and invalid cross-references.
- [ ] Do not infer new kernel concepts from unknown extension keys.
- [ ] Include `x-codegen` version/behavior and policy in source digest identity.

## OA-011 — Storage mapping normalization

- [ ] Normalize typed `x-codegen` persistence metadata into `group.storage.mappings`.
- [ ] Link each mapping to a known schema.
- [ ] Normalize stores, mapped fields, keys, indexes, relations, constraints, and documented metadata only through known kernel types.
- [ ] Validate mapped source fields and relation targets with source-spanned diagnostics.
- [ ] Do not create neutral entity/model/repository/ORM class objects.
- [ ] Preserve ORM/framework-specific metadata only through approved known fields or bounded extensions/raw values.

## OA-012 — View and interaction normalization

- [ ] Normalize typed `x-codegen` interaction metadata into `group.views`, parts, triggers, flows, and known access facts.
- [ ] Link triggers to known operations by semantic ID.
- [ ] Preserve explicit local event effects where represented by the known event contract.
- [ ] Validate missing operations, invalid ownership, duplicate view/part/trigger IDs, and flow transitions.
- [ ] Do not create neutral frontend/UI/page/screen/component/widget roots.
- [ ] Keep framework/layout/rendering syntax out of the adapter.

## OA-013 — Events, listeners, and delivery normalization

- [ ] Normalize typed event declarations into `group.events` with payload/context schema references.
- [ ] Normalize operation/workflow-caused occurrences into effects.
- [ ] Normalize known publication, consumption, channel, and protocol-binding facts into the events facet.
- [ ] Normalize listeners as ordinary operations with trigger facets.
- [ ] Distinguish event occurrence, payload/message, channel/delivery, and producer/consumer operation.
- [ ] Validate all event/channel/operation/schema references.
- [ ] Preserve unsupported protocol details only through bounded approved extensions/raw values.

## OA-014 — Execution hook normalization

- [ ] Normalize typed execution metadata into before, around, after_success, after_failure, and after_complete phases.
- [ ] Represent each hook as a reference to an ordinary operation plus order, condition, input/output bindings, and stop/failure behavior.
- [ ] Normalize group defaults and operation declarations separately so core can expose declared/effective values.
- [ ] Validate hook operations, phases, ordering, mappings, and cycles where prohibited.
- [ ] Do not create a separate arbitrary hook executable hierarchy.

## OA-015 — Workflow and compensation normalization

- [ ] Normalize typed workflow declarations into `group.workflows`.
- [ ] Normalize inputs, outputs, operation/decision/parallel/wait/end steps, transitions, failures, effects, and known facets.
- [ ] Link operation steps to one forward operation.
- [ ] Normalize optional compensation operation, input mappings, condition, retry, timeout, order, and failure policy.
- [ ] Preserve reverse-completed compensation semantics where declared/defaulted by the kernel contract.
- [ ] Distinguish local transaction facts from distributed compensation.
- [ ] Validate transitions, branches, waits/events, operation references, mappings, and unreachable/invalid structures according to core contracts.
- [ ] Do not generate Temporal, saga, Step Functions, queue, or service code.

## OA-016 — Provenance and bounded extensions/raw

- [ ] Attach source spans and canonical source paths to every normalized kernel object/relation where possible.
- [ ] Preserve approved unknown OpenAPI/`x-codegen` metadata only as safe immutable bounded values.
- [ ] Prevent parser objects, mutable mappings, resolver instances, OpenAPI library classes, or callables from entering IR.
- [ ] Add type, key, size, and depth limits and serialization tests.
- [ ] Prove preserved values cannot register facets/selectors/context properties or alter validation behavior.

## OA-017 — Adapter facade and digest

- [ ] Compose loader, parser, resolver, structural validator, `x-codegen` decoder, normalizers, and diagnostics behind the public source-adapter protocol.
- [ ] Produce immutable source result, diagnostics, closed-kernel IR, and source/behavior digest.
- [ ] Include all options, grouping rules, operation-ID policy, `x-codegen` schema/behavior, and authorized-loader behavior in digest identity.
- [ ] Support cancellation between documents, references, schemas, groups, operations, and typed metadata sections.
- [ ] Hand final semantic validation to core without bypassing source-specific diagnostics.

## OA-018 — Conformance and focused tests

- [ ] Pass shared source-adapter conformance.
- [ ] Add minimal OpenAPI 3.0/3.1 fixtures for every supported standard construct.
- [ ] Add focused `x-codegen` fixtures for stable IDs, storage, views, access, events/listeners, hooks, workflows, and compensation.
- [ ] Add invalid reference, cycle, duplicate, unsupported, path escape, unauthorized network, unknown facet/concept, and cancellation tests.
- [ ] Prove parse-once/reference-once behavior through instrumentation.
- [ ] Prove deterministic immutable kernel output and source-spanned diagnostics.
- [ ] Prove no semantic-kernel extension or target syntax leaks.

## OA-019 — Connected realistic and performance fixtures

- [ ] Use the realistic generated `openapi.v1.json`/equivalent source containing real `x-codegen` metadata as an inspectable regression fixture.
- [ ] Assert selected exact normalized groups, schemas, operations, HTTP/access facets, storage mappings, views, events/listeners, execution hooks, workflows, and compensation relationships.
- [ ] Integrate the fixture with official backend/SDK/Flutter/documentation packs.
- [ ] Assert exact semantic-to-artifact blast radius for selected source changes.
- [ ] Benchmark parse, reference resolution, typed metadata decoding, normalization, validation, memory, and cancellation latency.
- [ ] Avoid giant opaque snapshots; keep summaries and exact relationship assertions inspectable.

## OA-020 — Documentation and release

- [ ] Document supported OpenAPI versions/features and explicit unsupported behavior.
- [ ] Document supported `x-codegen` versions, schemas, mappings, and diagnostics.
- [ ] Document grouping and operation-ID policies.
- [ ] Document local, memory, and controlled external-reference policies.
- [ ] Document that adapters cannot extend the kernel or generate syntax.
- [ ] Build wheel/sdist and test independent installation/entry-point discovery.

## Completion gate

- shared source conformance passes;
- source is parsed and references resolved once per session;
- typed/versioned `x-codegen` metadata maps only into known kernel contracts;
- groups replace neutral resource assumptions;
- schemas remain structural and operation direction remains on schema uses;
- operations expose inputs, outputs, failures, effects, and known facets accurately;
- storage, views, access, events/listeners, hooks, workflows, and compensation relationships are validated;
- OpenAPI-specific types do not escape into core/adapters/templates;
- adapters cannot add semantic objects, facets, selectors, expressions, or contexts;
- unauthorized filesystem/network access is impossible through the adapter;
- output IR is deterministic, immutable, source-provenanced, and directly canonical.
