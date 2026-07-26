# Neutral IR, selection, path composition, and planning tasks

## IR-001 — Provenance and semantic identity

**Status:** planned

**Dependencies:** CORE-003, CORE-004

- [ ] Implement source-neutral document, node ID, semantic ID, provenance chain, and extension-key primitives.
- [ ] Preserve source spans without storing parser-specific objects.
- [ ] Implement stable hashing and deterministic ordering.

## IR-002 — Semantic names and type expressions

**Status:** planned

**Dependencies:** IR-001, PATH-001

- [ ] Implement semantic names independent from target-language rendering and output filenames.
- [ ] Expose typed case and original/singular/plural projections through the core naming contract.
- [ ] Do not add `fileName`, `filePath`, or `directory` properties to semantic items.
- [ ] Implement primitive, reference, array, map, tuple, union, intersection, nullable, optional, generic, literal, function, and unknown/unsupported diagnostic type forms.
- [ ] Keep optional presence distinct from nullable value.
- [ ] Add visitor/matcher contracts without language-specific imports.

## IR-003 — Schemas and operations

**Status:** planned

**Dependencies:** IR-002

- [ ] Implement schemas, fields, enums, DTO roles, entities, relationships, resources, operations, parameters, requests, responses, errors, and media representations.
- [ ] Implement dependency references by semantic ID.
- [ ] Add immutable validation and deterministic traversal.

## IR-004 — Bounded extensions

**Status:** planned

**Dependencies:** IR-003

- [ ] Define registered namespaced extension values for source provenance not belonging in core semantics.
- [ ] Prevent source-specific classes from escaping through extensions.
- [ ] Add serialization and size/depth limits.

## PLAN-001 — Pack source-file discovery descriptors

**Status:** planned

**Dependencies:** PACKCFG-002..PACKCFG-004, plugin target/engine registries

- [ ] Walk content roots deterministically.
- [ ] Apply ignore rules before descriptor creation.
- [ ] Preserve exact content-root-relative source paths including braces/brackets.
- [ ] Infer engine and target suffixes.
- [ ] Detect text versus binary safely.
- [ ] Apply descriptor patterns and exact settings to one descriptor.
- [ ] Validate explicit target/engine conflicts.
- [ ] Keep authored documentation and partials non-emitting by default.

## PLAN-002 — Selection compiler

**Status:** planned

**Dependencies:** IR-003, PACKCFG-004

- [ ] Compile once, each, grouped, aggregate, and artifact-derived selections.
- [ ] Implement bounded typed filters, projections, ordering, and grouping.
- [ ] Produce stable selection identities for cache keys.
- [ ] Diagnose missing fields and unsupported expressions before invocation creation.

## PLAN-003 — Named path recipe and source-tree fan-out

**Status:** planned

**Dependencies:** PLAN-001, PLAN-002, PATH-003..PATH-005

- [ ] Resolve `{recipe}` tokens left to right.
- [ ] Apply structural, selection-only, and selection-plus-parts recipes.
- [ ] Scope nested aliases and validate prior-alias requirements.
- [ ] Preserve literal relative source structure after recipe expansion.
- [ ] Fan out templates, static text, and binary files consistently.
- [ ] Apply descriptor-pattern specificity independently from destination composition.
- [ ] Reject recursive recipes, alias shadowing, cycles, and duplicate invocations.

## PLAN-004 — Template invocation model

**Status:** planned

**Dependencies:** PLAN-001..PLAN-003, RULE/BIND tasks

- [ ] Implement invocation identity, selected context, effective target/engine rules, bindings, imports, includes, outputs, lifecycle, and profile state.
- [ ] Resolve one target and one engine per template invocation.
- [ ] Implement aggregate/monolithic invocation.
- [ ] Implement multiple predeclared named outputs.

## PLAN-005 — Includes and partial graph

**Status:** planned

**Dependencies:** PLAN-004, engine port

- [ ] Resolve includes through the pack template registry.
- [ ] Validate same-target or neutral partial compatibility.
- [ ] Detect cycles and depth violations before rendering.
- [ ] Disable undeclared dynamic includes by default.

## PLAN-006 — Provider and artifact graph

**Status:** planned

**Dependencies:** PLAN-004

- [ ] Implement typed capabilities, providers, requirements, and artifact references.
- [ ] Detect missing, duplicate, and ambiguous providers.
- [ ] Support cross-pack capability references through declared pack dependencies.
- [ ] Compute deterministic topological order.

## PLAN-007 — Imports, exports, and authored barrels

**Status:** planned

**Dependencies:** PLAN-006, BIND tasks, language port

- [ ] Create semantic import requests from artifact and binding references.
- [ ] Resolve project paths, package paths, modules, namespaces, aliases, and barrels through the target adapter.
- [ ] Deduplicate and alias collisions deterministically.
- [ ] Create immutable export descriptors for authored barrel templates.
- [ ] Prove comments/custom text remain owned by the barrel template.
- [ ] Ensure import planning consumes resolved artifact paths but does not choose output paths.

## PLAN-008 — Source-path output and lifecycle graph

**Status:** planned

**Dependencies:** PLAN-004, PATH-005..PATH-007

- [ ] Compile the content-root-relative source path as the default output expression.
- [ ] Resolve `[expression]`, escaping, name projections, and recipe output parts.
- [ ] Strip only the engine suffix and preserve target suffixes.
- [ ] Support exceptional explicit output and predeclared named outputs through the same grammar.
- [ ] Reject traversal, absolute escape, invalid segments, symlink escape, target filename violations, and platform case collisions.
- [ ] Detect duplicate destinations before render.
- [ ] Resolve managed, immutable, protected, and unmanaged intent with project/host restrictions.

## PLAN-009 — Commands, contributions, and readiness

**Status:** planned

**Dependencies:** CMD, ECO, SETUP contracts

- [ ] Add dependency/manifest contributions to the plan.
- [ ] Add typed actions and raw commands with ownership, phase, capabilities, and approval state.
- [ ] Add manual steps and unresolved binding actions.
- [ ] Compute ready, warning, actions, partial, failed, or cancelled status.

## PLAN-010 — Plan inspection and serialization

**Status:** planned

**Dependencies:** PLAN-001..PLAN-009, PATH-009

- [ ] Produce stable human and structured plan views.
- [ ] Include source/pack/plugin versions, effective rules, source paths, parsed tokens, recipe expansions, selections, graph edges, outputs, commands, approvals, and actions.
- [ ] Exclude secrets.
- [ ] Add deterministic snapshots for small fixtures.

## Acceptance gate

- IR has no OpenAPI, TypeScript, Dart, Jinja, filesystem, command, or CLI imports.
- Semantic items expose names and meaning, not generated filenames.
- A heterogeneous pack plans tokenized templates, static files, binary files, partials, and authored barrels.
- Invalid plans never call renderers or writers.
- All graph/path diagnostics identify source descriptors, token spans, aliases, and related providers.
- One aggregate template can plan a single complete generated file.
- Every normal output can be explained from the pack source path plus named recipes and typed values.
