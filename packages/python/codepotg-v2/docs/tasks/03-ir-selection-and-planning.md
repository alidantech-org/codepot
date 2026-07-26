# Neutral IR, fixed selections, filesystem discovery, and planning tasks

## IR-001 — Provenance and semantic identity

**Status:** planned

**Dependencies:** CORE-003, CORE-004

- [ ] Implement source-neutral document, node ID, semantic ID, provenance, and extension-key primitives.
- [ ] Preserve source spans without parser-specific objects.
- [ ] Implement stable hashing and deterministic ordering.

## IR-002 — Semantic names and type expressions

**Status:** planned

**Dependencies:** IR-001, PATH-001

- [ ] Implement semantic names independent from target rendering and output filenames.
- [ ] Expose documented case and original/singular/plural projections.
- [ ] Do not add `fileName`, `filePath`, or `directory` properties.
- [ ] Implement neutral primitive/reference/collection/union/function/unsupported type forms.
- [ ] Keep optional presence distinct from nullable value.

## IR-003 — Schemas, resources, and operations

**Status:** planned

**Dependencies:** IR-002

- [ ] Implement schemas, fields, enums, DTO/model roles, entities, relations, resources, operations, parameters, requests, responses, and errors.
- [ ] Implement dependency references by semantic ID.
- [ ] Add immutable validation and deterministic traversal.
- [ ] Expose the normalized collections required by the fixed selector registry.

## IR-004 — Bounded extensions

**Status:** planned

**Dependencies:** IR-003

- [ ] Define registered namespaced extension values for source provenance not belonging in core semantics.
- [ ] Prevent source-specific classes from escaping through extensions.
- [ ] Add serialization and size/depth limits.

## PLAN-001 — Filesystem discovery descriptors

**Status:** planned

**Dependencies:** PACKCFG-002..PACKCFG-004, target/engine registries

- [ ] Walk the default `templates/` root deterministically.
- [ ] Apply pack-root `.gitignore`, `include`, and `exclude` before descriptor creation.
- [ ] Preserve exact relative paths including braces, parentheses, and literal brackets.
- [ ] Classify `_partials/**` as non-emitting.
- [ ] Infer engine and target suffixes.
- [ ] Detect text versus binary safely.
- [ ] Treat literal `.gitignore` as discovery control and `.gitignore.jinja` as an emitting template.

## PLAN-002 — Fixed selector compiler

**Status:** planned

**Dependencies:** IR-003, PACKCFG-004, PATH-006

- [ ] Compile the versioned fixed selector registry.
- [ ] Implement `.each` and `.all` cardinality.
- [ ] Infer stable singular/plural context names.
- [ ] Implement optional inline aliases.
- [ ] Implement parent-scoped selectors such as `resource.entities.each`.
- [ ] Produce stable selector/scope identities for cache and lock behavior.
- [ ] Reject arbitrary pack-defined `from`/`as`, unknown selectors, and invalid parent scopes.

## PLAN-003 — Selection-folder source-tree expansion

**Status:** planned

**Dependencies:** PLAN-001, PLAN-002, PATH-003..PATH-005

- [ ] Parse whole `{selectionKey}` folder segments and built-in `{root}`.
- [ ] Resolve registered selection `paths` arrays relative to the pack output root.
- [ ] Establish fixed selector contexts before resolving later expressions.
- [ ] Evaluate nested selection folders left to right.
- [ ] Preserve literal relative structure after selection-folder expansion.
- [ ] Fan out templates, static text, and binary files consistently.
- [ ] Reject missing keys, shadowing, selector cycles, and duplicate invocations.

## PLAN-004 — Template invocation model

**Status:** planned

**Dependencies:** PLAN-001..PLAN-003, RULE/BIND tasks

- [ ] Implement invocation identity, active selector contexts, target/engine, options, external bindings, generated imports, exports, symbols, and lifecycle state.
- [ ] Resolve one target and one engine per template invocation.
- [ ] Support ordinary repeated templates, `.all` aggregate templates, and export/barrel templates.
- [ ] Keep outputs fixed before rendering.

## PLAN-005 — Includes and partial graph

**Status:** planned

**Dependencies:** PLAN-004, engine port

- [ ] Resolve includes only through the discovered `_partials` registry.
- [ ] Validate target-neutral or compatible partial use.
- [ ] Detect cycles and depth violations before rendering.
- [ ] Disable undeclared dynamic filesystem includes.

## PLAN-006 — Selection dependency and symbol graph

**Status:** planned

**Dependencies:** PLAN-004, BIND-002

- [ ] Build graph nodes from registered selection keys and their planned emissions.
- [ ] Resolve explicit `imports: localName: selectionKey` edges.
- [ ] Resolve ordered `exports: [selectionKey]` edges, including barrels exporting barrels.
- [ ] Match semantic requirements to explicitly declared `symbols`.
- [ ] Preserve global, `.all`, `.each`, and parent scope.
- [ ] Reject missing providers, ambiguous scopes, duplicate/conflicting symbols, and cycles.
- [ ] Compute deterministic topological order.

## PLAN-007 — Language-neutral import/export plans

**Status:** planned

**Dependencies:** PLAN-006, language port

- [ ] Compute the least-required symbols for each consumer invocation.
- [ ] Distinguish direct multi-file providers from aggregate and barrel providers.
- [ ] Supply final planned source/destination paths, symbols, scope, and local import name to language adapters.
- [ ] Create immutable ordered export descriptors for authored barrel templates.
- [ ] Ensure target adapters calculate syntax/module paths but never output directories.
- [ ] Keep comments and textual export ordering owned by authored templates.

## PLAN-008 — Output and collision graph

**Status:** planned

**Dependencies:** PLAN-004, PATH-005..PATH-008

- [ ] Compile literal paths, selection folders, `(expression)`, and `((literal))` into pack-relative destinations.
- [ ] Leave square brackets literal for framework routes.
- [ ] Strip only the engine suffix and preserve target suffixes.
- [ ] Prepend the pack-instance output root.
- [ ] Reject traversal, absolute/root escape, invalid segments, symlink escape, target filename violations, and platform collisions.
- [ ] Detect duplicate destinations before rendering.

## PLAN-009 — Commands, approvals, and readiness

**Status:** planned

**Dependencies:** CFG-004..CFG-005, CMD, SETUP contracts

- [ ] Add exact project and pack commands with executable resolution, opaque argument lists, phase, capabilities, and approval state.
- [ ] Do not derive commands from dependency metadata.
- [ ] Add unresolved bindings and manual actions.
- [ ] Compute ready, warning, actions, failed, or cancelled status.

## PLAN-010 — Plan inspection and serialization

**Status:** planned

**Dependencies:** PLAN-001..PLAN-009, PATH-009

- [ ] Produce stable human and structured plan views.
- [ ] Include source/pack/plugin identities, source paths, selection folders, fixed selectors, contexts, expressions, outputs, import/export graph, symbols, commands, and approvals.
- [ ] Exclude secrets and credentials.
- [ ] Add deterministic snapshots using the checked-in example configurations.

## Acceptance gate

- IR has no OpenAPI, TypeScript, Dart, Jinja, filesystem, command, or CLI imports.
- Semantic items expose meaning and names, not generated filenames.
- Literal templates/static files require no manifest file registry.
- Fixed selectors and selection folders plan TypeORM, TypeScript SDK, and Flutter SDK fixtures.
- Generated imports and barrels resolve only through declared selection keys and symbols.
- Invalid plans never call renderers or writers.
- Every output can be explained from the pack filesystem, selection registry, expressions, and project output root.
