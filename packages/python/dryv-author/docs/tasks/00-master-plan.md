# dryv-author master implementation plan

The package compiles concise typed Python declarations into the existing closed Codepot IR and canonical JSON/YAML. It must not become a second semantic graph, runtime DSL, generator, writer, or framework binding system.

## AUTHOR-001 — Package foundation

**Status:** planned

- [ ] Finalize package metadata, dependencies, typing marker, public version, README, license, source/test layout, and build configuration.
- [ ] Add import-smoke and wheel-content tests.
- [ ] Prove import has no filesystem, environment, network, plugin discovery, compilation, or global-registry side effects.

## AUTHOR-002 — Immutable author options and behavior versions

**Status:** planned

- [ ] Define frozen typed options for ID policy, strictness, Pydantic interpretation, derivation behavior, limits, transport formatting, and unsupported-core policy.
- [ ] Reject unknown options and wrong value types.
- [ ] Version every output-affecting author/compiler behavior.
- [ ] Exclude target language, framework, pack, selector, template, path, writer, and command options.

## AUTHOR-003 — Author session and declaration registry

**Status:** planned

- [ ] Implement explicit `Author` session ownership.
- [ ] Add session-scoped registries by known declaration kind.
- [ ] Support multiple independent contracts in one process.
- [ ] Freeze registries before compilation.
- [ ] Reject declaration mutation after freeze.
- [ ] Prove no process-global decorator/ref/model registry exists.

## AUTHOR-004 — Provenance and structured diagnostics

**Status:** planned

- [ ] Capture Python module/file/line/column and declaration paths where safely available.
- [ ] Define stable AUTHOR diagnostic families.
- [ ] Convert expected Pydantic, selector, linker, compiler, and transport failures into diagnostics.
- [ ] Redact credentials, unstable tracebacks, object addresses, and absolute temporary paths.

## AUTHOR-005 — Names, IDs, duplicate policy, and deterministic ordering

**Status:** planned

- [ ] Assign deterministic declaration identities and core `SemanticId` values.
- [ ] Validate explicit IDs and group ownership.
- [ ] Detect duplicates before construction.
- [ ] Define stable ordering independent from mutable hash maps.
- [ ] Reuse public core naming projections rather than inventing author-only naming semantics.

## AUTHOR-006 — Typed ref foundations

**Status:** planned

- [ ] Implement immutable generic ref identities and kind-specific public wrappers.
- [ ] Bind every ref to one author session.
- [ ] Reject foreign-session refs and wrong-kind refs.
- [ ] Keep refs non-serializable as final IR values.
- [ ] Add equality/hash/repr rules that expose no target object or memory address.

## AUTHOR-007 — Ref usages, aliases, and forward refs

**Status:** planned

- [ ] Implement immutable optional/required, nullable/non-nullable, array/single, and supported extension/projection usage wrappers.
- [ ] Implement explicit typed forward declaration/definition.
- [ ] Resolve aliases without duplicating semantic targets.
- [ ] Detect missing, duplicate, cyclic, incompatible, and unresolved refs.
- [ ] Add instrumentation proving each ref resolves once per compile session.

## AUTHOR-008 — Static typing contract

**Status:** planned

- [ ] Add strict Pyright configuration and positive/negative fixtures.
- [ ] Add strict mypy configuration or document exact supported differences.
- [ ] Prove wrong ref kinds, unknown field selector attributes, incompatible workflow refs, and invalid builder arguments fail static checks.
- [ ] Avoid public `Any` escape hatches.

## AUTHOR-009 — Reusable properties and primitive authoring

**Status:** planned

- [ ] Define reusable primitive/property declarations with types, formats, constraints, defaults/examples, docs, provenance, and supported tags/guidance.
- [ ] Support ordinary `Annotated` aliases and explicit property refs.
- [ ] Compile into structural core schema/type facts without OpenAPI or Zod models.
- [ ] Reject arbitrary Pydantic core schema objects in IR.

## AUTHOR-010 — Enum, alias, collection, union, and composite schemas

**Status:** planned

- [ ] Compile Python enums and typed declarations into structural enum schemas.
- [ ] Support aliases, arrays, maps, tuples, unions, intersections where public core supports them.
- [ ] Preserve optional versus nullable semantics.
- [ ] Validate duplicate enum values and unsupported arbitrary objects.

## AUTHOR-011 — Pydantic model compiler

**Status:** planned

- [ ] Support Pydantic v2 `BaseModel` subclasses and approved author base model.
- [ ] Interpret fields, annotations, defaults, requiredness, nested models, enums, collections, unions, and `Annotated` Codepot metadata.
- [ ] Detect recursive models through refs without infinite expansion.
- [ ] Convert unsupported validators/computed/runtime behavior into exact diagnostics.
- [ ] Ensure Pydantic classes never enter core IR or template contexts.

## AUTHOR-012 — Typed field selector engine

**Status:** planned

- [ ] Implement restricted typed selector proxies for fields.
- [ ] Support single/tuple selections for pick, omit, storage, source, view, and operation helpers.
- [ ] Reject unknown attributes, foreign schema fields, non-field values, and arbitrary callback behavior.
- [ ] Add type-checker fixtures for selector safety.

## AUTHOR-013 — Schema projections and derivations

**Status:** planned

- [ ] Implement pick, omit, partial, extend, and alias projection chains.
- [ ] Implement explicit create/update/read/query derivation authoring.
- [ ] Record source schema, steps, fields, behavior version, and provenance.
- [ ] Compile every result into ordinary structural schemas.
- [ ] Add exact debug and relationship tests; no entity/model/request/response schema kinds.

## AUTHOR-014 — Field capabilities and reference authoring

**Status:** blocked on public core field-capability contracts

- [ ] Define typed author declarations for initialization, mutation, visibility/sensitivity, query operators, sort/select capability, and field reference.
- [ ] Keep capabilities dormant until an operation/view explicitly uses them.
- [ ] Compile only into published core field facets.
- [ ] Never encode unsupported capabilities into arbitrary extensions/raw.

## AUTHOR-015 — Storage mapping authoring

**Status:** planned

- [ ] Create storage mappings from schema refs with deterministic same-name field mapping helpers.
- [ ] Support explicit fields, source/store names, primary keys, indexes, uniqueness, nullability, and supported relation facts.
- [ ] Keep stored/generated/computed/absent behavior mapping-relative.
- [ ] Do not create entity/repository/ORM objects or target-specific declarations.

## AUTHOR-016 — Policies and access authoring

**Status:** planned

- [ ] Define reusable policy refs and concise known access-facet builders.
- [ ] Compile only public core policy/access facts.
- [ ] Resolve declared/effective relationships only through core rules.
- [ ] Do not add a generic Python predicate language.

## AUTHOR-017 — Events and operation effects

**Status:** planned

- [ ] Define events with payload/context schema refs and version/source facts.
- [ ] Compile caused occurrences into operation/workflow effects.
- [ ] Validate every event/schema/operation relationship.
- [ ] Keep delivery/runtime syntax out of authoring.

## AUTHOR-018 — Operation core authoring

**Status:** planned

- [ ] Define operations, inputs, outputs, failures, effects, docs, tags/guidance, and known facets.
- [ ] Add concise query/command/listener/scheduled helpers that return ordinary operation refs.
- [ ] Preserve schema-use direction and use-specific required/nullable facts.
- [ ] Reject operation IDs, input names, output names, and failure codes that conflict.

## AUTHOR-019 — HTTP facet authoring

**Status:** planned for current public subset; extended bindings blocked on core

- [ ] Compile method/path/operation ID supported by current core.
- [ ] Add concise neutral input/output binding declarations only when public core supports them.
- [ ] Support path/query/header/cookie/body/status/media/header/cookie facts only through published facet fields.
- [ ] Never expose runtime request/response objects or framework middleware/controller APIs.

## AUTHOR-020 — Trigger and execution authoring

**Status:** planned

- [ ] Define event/schedule/interaction/storage/system trigger helpers supported by core.
- [ ] Define execution hooks referencing ordinary operations with phase/order/condition/stop facts.
- [ ] Validate operation refs, phases, ordering, and cycles according to public contracts.

## AUTHOR-021 — Value sources

**Status:** blocked on public core `ValueSource`

- [ ] Define operation-backed source authoring with item/value/label and optional dependent input facts.
- [ ] Validate operation output and field refs.
- [ ] Keep sources neutral to HTTP, frontend fetch code, database joins, and UI controls.
- [ ] Compile only after core publishes object, validation, selectors, and contexts.

## AUTHOR-022 — Views and parts

**Status:** planned for current public subset

- [ ] Define group-owned views, nested parts, schemas, triggers, access, docs, tags/guidance, and source uses supported by core.
- [ ] Validate nested IDs and operation/schema/source refs.
- [ ] Avoid page/screen/component/widget kernel vocabulary.

## AUTHOR-023 — Presentations and placements

**Status:** blocked on public core `Presentation`

- [ ] Define contract-level presentation identity and neutral channel.
- [ ] Place views across groups without copying them.
- [ ] Define typed addresses and navigation relationships.
- [ ] Validate presentation/view/address/navigation refs.
- [ ] Compile only after core publishes models, selectors, contexts, and version rules.

## AUTHOR-024 — Workflows

**Status:** planned

- [ ] Define workflow inputs, outputs, failures, effects, facets, and typed refs.
- [ ] Add operation, decision, parallel, wait, and end step helpers.
- [ ] Add transitions and optional compensation operation facts.
- [ ] Validate step names, targets, branches, waits/events, refs, and unreachable/invalid structures through core validation.

## AUTHOR-025 — Tags

**Status:** blocked on public core `TagSet`

- [ ] Implement namespaced tag validation and immutable authoring API.
- [ ] Compile tags into shared kernel data on supported objects.
- [ ] Expose safe immutable template methods through core-prepared context.
- [ ] Include tags in transport and digest.
- [ ] Never use tags as refs, relationships, typed-field replacements, or key/value programming.

## AUTHOR-026 — Categorized guidance/info

**Status:** blocked on public core guidance contract

- [ ] Implement fluent explain/implement/warn/security/persistence/caching/testing/observability/UX/accessibility and custom approved categories.
- [ ] Deduplicate and deterministically order notes.
- [ ] Preserve guidance in IR/transport/context.
- [ ] Prove guidance does not silently create semantic behavior.

## AUTHOR-027 — Multi-pass compiler and `AuthoringResult`

**Status:** planned

- [ ] Implement explicit compiler context and ordered subsystem passes.
- [ ] Compile each declaration/ref exactly once.
- [ ] Construct only public core IR values.
- [ ] Run final core validation.
- [ ] Return immutable contract, diagnostics, and digest.
- [ ] Add cancellation/limits only when a public author API defines them; no hidden runtime threads.

## AUTHOR-028 — Canonical JSON/YAML transport

**Status:** planned; core codec ownership must be resolved explicitly

- [ ] Define versioned canonical IR envelope and strict typed document model.
- [ ] Encode/decode every supported core IR value and relation.
- [ ] Use safe duplicate-key-aware YAML.
- [ ] Prove JSON/YAML parity and exact round trips.
- [ ] Validate after decode and expose structured transport diagnostics.
- [ ] Keep authoring state/Pydantic/callables out of documents.
- [ ] Make canonical JSON the digest/signature representation.

## AUTHOR-029 — Connected fixtures, conformance, performance, and distribution

**Status:** planned

- [ ] Build small fixtures for every subsystem.
- [ ] Build one realistic cross-group contract containing schemas, projections, storage, policies, events, operations, HTTP, views, workflows, and every core-supported approved feature.
- [ ] Add architecture, contracts, typing, unit, integration, transport, distribution, and performance tests.
- [ ] Benchmark compile/link/validation/serialization and repeated no-state-leak behavior.
- [ ] Build wheel/sdist and test isolated installation.

## AUTHOR-030 — Documentation and release

**Status:** planned

- [ ] Document public API, typing support, ref engine, Pydantic support, derivation, diagnostics, transport format, blockers, and explicit non-goals.
- [ ] Add runnable examples and migration notes for promoted tags/core changes.
- [ ] Record exact tests, builds, digests, and package compatibility.

## Completion gate

- authoring compiles only into public closed IR;
- no process-global registries or import-time compilation;
- typed refs and selector proxies have static and runtime tests;
- Pydantic never leaks into IR or template contexts;
- derivations compile into normal structural schemas;
- unsupported core concepts fail explicitly rather than entering extensions;
- canonical JSON/YAML round trips exactly and can be shipped as direct semantic input;
- output is deterministic, immutable, readable, and core-valid;
- no OpenAPI, target language, framework, pack, template, writer, CLI, command, or old-runtime ownership exists;
- full lint, format, typing, tests, build, and isolated installation pass;
- working tree is clean and exact evidence is recorded.
