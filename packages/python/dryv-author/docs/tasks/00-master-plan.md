# dryv-author master plan

`dryv-author` compiles concise typed Python declarations into the public immutable `dryv.ir.Contract`. It is an authoring frontend, not a second semantic graph, generator, writer, transport owner, CLI, or framework binding system.

## AUTHOR-001 — Package foundation

- [x] Package metadata, typed marker, source/test layout, and public imports.
- [x] Import-side-effect, architecture, wheel, and distribution tests.
- [ ] Finalize release metadata after the Dryv package split stabilizes.

## AUTHOR-002 — Author sessions and immutable options

- [x] Explicit `Author` session ownership.
- [x] Frozen typed options and unsupported-core policy.
- [x] Session-scoped declaration and reference state.
- [x] No process-global registry or import-time compilation.

## AUTHOR-003 — Diagnostics and provenance

- [x] Stable author diagnostic models backed by public Dryv diagnostics.
- [x] Declaration paths and source context where safely available.
- [x] Expected validation/linking/compiler failures converted into diagnostics.
- [ ] Expand source-position coverage without exposing unstable temporary paths.

## AUTHOR-004 — Typed references

- [x] Kind-specific immutable references.
- [x] Foreign-session, missing, duplicate, and wrong-kind rejection.
- [x] Immutable optional, nullable, collection, and projection usages.
- [x] Deterministic linking and ordering.
- [ ] Add an explicit future import/export contract before allowing cross-module refs.

## AUTHOR-005 — Structural schema authoring

- [x] Reusable properties and fields.
- [x] Structural object, enum, alias, collection, union, and composite support within the public core contract.
- [x] Optional and nullable semantics remain distinct.
- [x] No framework, database, request, response, model, or entity kernel roots.

## AUTHOR-006 — Pydantic compilation

- [x] Pydantic v2 model and field interpretation.
- [x] Nested models, enums, collections, unions, defaults, and annotations.
- [x] Deterministic recursive-model handling through refs.
- [x] Pydantic classes and runtime validators never enter IR or template contexts.

## AUTHOR-007 — Projections and derivation

- [x] Pick, omit, partial, extend, and projection chains.
- [x] Explicit create, update, read, and query derivation helpers.
- [x] Every result compiles into ordinary structural schemas.
- [ ] Improve provenance inspection exposed by the runtime plan/debug APIs.

## AUTHOR-008 — Semantic builders

- [x] Operations, inputs, outputs, failures, and effects.
- [x] Storage mappings, policies, events, views, and workflows supported by the public IR.
- [x] Typed reference validation across those declarations.
- [ ] Add builders only when new public Dryv semantic contracts are published.

## AUTHOR-009 — Tags, guidance, value sources, and presentations

- [x] Compile the subset currently published by the Dryv kernel.
- [ ] Keep unsupported concepts fail-closed with exact diagnostics.
- [ ] Never hide unsupported semantics in raw dictionaries or private extension bags.

## AUTHOR-010 — Compiler pipeline

- [x] Explicit deterministic compiler passes.
- [x] Freeze declarations before compilation.
- [x] Compile each declaration and ref exactly once per session.
- [x] Construct only public Dryv IR values.
- [x] Run final core validation.
- [x] Return an immutable contract and diagnostics.

## AUTHOR-011 — Runtime-owned transport

- [x] Author compilation returns an in-memory `Contract`.
- [x] Author transport helpers delegate to the canonical Dryv codec.
- [ ] Remove remaining compatibility exports after callers migrate.
- [ ] Expose JSON/YAML emission through `dryv` and `dryv-cli`, not a second author codec.

## AUTHOR-012 — Static typing

- [x] Strict Pyright configuration and fixtures.
- [x] Strict mypy configuration and fixtures.
- [x] Positive and negative typed-reference cases.
- [ ] Expand static coverage for future semantic builders without adding `Any` escape hatches.

## AUTHOR-013 — Tests and distribution

- [x] Unit, integration, architecture, typing, performance, and distribution suites.
- [x] Deterministic repeated and concurrent-session checks.
- [x] Wheel/sdist and isolated-install coverage.
- [ ] Re-run the complete release matrix after the final Dryv runtime and CLI split.

## AUTHOR-014 — Documentation and cookbook

- [x] Public README and design boundaries.
- [ ] Add focused cookbook recipes for schemas, refs, projections, operations, storage, views, and workflows.
- [ ] Add migration notes from archived Codepot authoring APIs.
- [ ] Document the direct in-memory runtime integration once the contract-provider API is published.

## Completion gate

- authoring compiles only into public closed Dryv IR;
- no process-global registries or import-time compilation;
- typed refs have static and runtime tests;
- Pydantic never leaks into IR or templates;
- derivations compile into normal structural schemas;
- unsupported core concepts fail explicitly;
- canonical transport is owned by the Dryv runtime;
- no target language, framework, pack, template, writer, CLI, or command ownership;
- lint, formatting, typing, tests, build, and isolated installation pass;
- release evidence records the exact commit and tool versions.
