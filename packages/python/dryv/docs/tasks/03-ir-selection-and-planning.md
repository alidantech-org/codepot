# Closed semantic kernel, root-first selections, and planning tasks

All tasks in this ledger implement the approved closed kernel in `../00-governance/04-closed-semantic-kernel.md`. No task may add adapter-defined semantic objects/facets, generic fact bags, arbitrary graph-query selectors, or language-rendered source syntax.

## IR-001 — Provenance and semantic identity

**Status:** planned

**Dependencies:** CORE-003, CORE-004

- [ ] Implement source-neutral contract/document ID, semantic ID, node ID, provenance, and source-span primitives.
- [ ] Preserve source locations without parser-specific objects.
- [ ] Implement stable hashing, equality, and deterministic ordering.
- [ ] Distinguish authored stable IDs from name/path-derived identities.
- [ ] Never guess that delete-plus-add is a rename when no stable source identity exists.

## IR-002 — Semantic names, type expressions, and schema structure

**Status:** planned

**Dependencies:** IR-001, PATH-001

- [ ] Implement semantic names using `x.name.{casing}.{number}`.
- [ ] Expose documented case and original/singular/plural projections with `o/s/p` aliases.
- [ ] Do not add `fileName`, `filePath`, `directory`, language class-name, or field-name convenience properties.
- [ ] Implement structural schema kinds: primitive, literal, enum, object, array, map, tuple, union, intersection, alias, and unknown.
- [ ] Implement fields, schema references, controlled schema roles such as explicit `dto`, and presence-aware constraints.
- [ ] Keep optional presence distinct from nullable value.
- [ ] Reject `model`, `entity`, request/response, class/interface/type/struct/record, and framework terms as schema kinds.

## IR-003 — Groups and schema-use relationships

**Status:** planned

**Dependencies:** IR-002

- [ ] Implement `contract.groups` and nested group containment.
- [ ] Implement group name/path, schemas, operations, views, storage, workflows, policies, events, known facets, documentation, extensions, and raw/provenance fields.
- [ ] Implement immutable schema-use records so direction belongs to the relation rather than permanently to the schema.
- [ ] Preserve stable group ownership for every child semantic object.
- [ ] Do not implement `resource`, service, module, feature, frontend, or UI as neutral root objects.

## IR-004 — Operation core

**Status:** planned

**Dependencies:** IR-003

- [ ] Implement operation name, inputs, outputs, failures, effects, documentation, provenance, extensions, and raw values.
- [ ] Link all schema uses by semantic identity.
- [ ] Keep HTTP query/path/header/body/status/media information out of the neutral operation core.
- [ ] Implement immutable deterministic traversal and relationship indexes.
- [ ] Validate duplicate input/output/failure identities and unresolved schema uses.

## IR-005 — Closed known facets

**Status:** planned

**Dependencies:** IR-004

- [ ] Implement a closed typed facet registry owned by core.
- [ ] Implement initial operation facets: HTTP, access, trigger, execution, and events.
- [ ] Implement documented workflow/group/view facet attachment locations.
- [ ] Reject unknown facet names and invalid attachment locations.
- [ ] Prevent source adapters, packs, language adapters, or third-party plugins from registering semantic facets.
- [ ] Expose immutable typed facet contexts rather than string-keyed facts.

## IR-006 — Views, storage mappings, and access policies

**Status:** planned

**Dependencies:** IR-003, IR-005

- [ ] Implement group views with parts, triggers, flows, operation references, access facet, documentation, extensions, and provenance.
- [ ] Implement `group.storage.mappings` with schema/store references, mapped fields, keys, indexes, relations, constraints, documentation, extensions, and provenance.
- [ ] Implement reusable `group.policies` with public/authenticated, roles, permissions, scopes, ownership/context conditions, and policy references.
- [ ] Resolve declared/effective access values for group/operation/workflow/view contexts.
- [ ] Do not implement neutral frontend/UI/page/screen/component/widget/entity objects.

## IR-007 — Events, listeners, and execution hooks

**Status:** planned

**Dependencies:** IR-004..IR-006

- [ ] Implement `group.events` declarations with payload/context schema references and stable identity.
- [ ] Implement operation/workflow event effects as caused occurrences.
- [ ] Implement known event trigger and delivery/publication/consumption facts under typed facets.
- [ ] Model listeners as operations with known trigger facets, not a parallel executable hierarchy.
- [ ] Implement execution phases: before, around, after_success, after_failure, and after_complete.
- [ ] Represent hooks as ordered/conditional references to ordinary operations with typed bindings and stop/failure behavior.
- [ ] Resolve group execution defaults into declared/effective operation execution contexts.

## IR-008 — Workflows, steps, transitions, and compensation

**Status:** planned

**Dependencies:** IR-004, IR-005, IR-007

- [ ] Implement `group.workflows` with inputs, outputs, steps, transitions, failures, effects, facets, documentation, extensions, and provenance.
- [ ] Implement known step structures: operation, decision, parallel, wait, and end.
- [ ] For operation steps, require one forward operation and allow one optional compensation record.
- [ ] Implement compensation operation reference, input mappings, condition, retry, timeout, order, and failure policy.
- [ ] Distinguish compensation from exact rollback and from local atomic transaction facts.
- [ ] Support reverse-completed compensation order and explicit alternatives only through typed kernel values.
- [ ] Validate transition targets, reachability rules, operation references, event waits, branches, and compensation mappings.

## IR-009 — Bounded extensions and raw provenance

**Status:** planned

**Dependencies:** IR-003..IR-008

- [ ] Define bounded namespaced extension values for source metadata not belonging in core semantics.
- [ ] Preserve explicitly authorized raw immutable values only where the kernel documents an escape hatch.
- [ ] Prevent source-specific classes, mutable mappings, resolvers, parser nodes, or callables from escaping.
- [ ] Add serialization, type, size, and depth limits.
- [ ] Prove extensions cannot add facets, selectors, expression roots, validators, or template-context properties.

## IR-010 — Kernel validation and typed graph indexes

**Status:** planned

**Dependencies:** IR-001..IR-009

- [ ] Implement one uniform diagnostic runner for all kernel concepts and relationships.
- [ ] Build internal typed indexes for group containment, schema references, operation uses, view triggers, storage relations, policy uses, execution hooks, events, workflows, transitions, and compensation.
- [ ] Keep graph implementation private; public/template APIs remain typed objects.
- [ ] Reject missing references, invalid ownership, unknown facets, cycles where prohibited, and incompatible mappings.
- [ ] Produce deterministic validation order and related source locations.

## PLAN-001 — Filesystem discovery descriptors

**Status:** planned

**Dependencies:** PACKCFG-002..PACKCFG-004, target/engine registries

- [ ] Walk the default `templates/` root deterministically.
- [ ] Apply pack-root `.gitignore`, `include`, and `exclude` before descriptor creation.
- [ ] Preserve exact relative paths including braces, parentheses, and literal brackets.
- [ ] Classify `_partials/**` as non-emitting.
- [ ] Infer engine and target suffixes.
- [ ] Detect text versus binary safely.
- [ ] Treat literal `.gitignore` as discovery control and `.gitignore.jinja` as emitting.

## PLAN-002 — Root-first fixed selector compiler

**Status:** planned

**Dependencies:** IR-010, PACKCFG-004, PATH-006

- [ ] Compile the versioned fixed selector registry from core-owned typed descriptors.
- [ ] Implement preferred selectors beginning with `groups` and active-parent selectors beginning with `group`.
- [ ] Implement `.each` and `.all` cardinality.
- [ ] Infer stable singular/plural context names and optional inline aliases.
- [ ] Preserve active outer-to-inner contexts for child selectors.
- [ ] Support global selectors only for documented project-wide use and surface discouragement in introspection/docs.
- [ ] Produce stable selector/scope identities for cache and generation-state behavior.
- [ ] Reject `resource`, `model`, `entity`, frontend/UI, reversed-root, arbitrary `where/traverse/depth`, and pack-defined selector grammar.

## PLAN-003 — Selection-folder source-tree expansion

**Status:** planned

**Dependencies:** PLAN-001, PLAN-002, PATH-003..PATH-005

- [ ] Parse whole `{selectionKey}` folder segments and built-in `{root}`.
- [ ] Resolve registered selection `paths` arrays relative to the pack output root.
- [ ] Establish fixed root-first selector contexts before resolving later expressions.
- [ ] Evaluate nested selection folders left to right.
- [ ] Preserve literal relative structure after selection-folder expansion.
- [ ] Fan out templates, static text, and binary files consistently.
- [ ] Reject missing keys, context shadowing, selector cycles, duplicate invocations, and reversed scopes.

## PLAN-004 — Invocation and artifact identity

**Status:** planned

**Dependencies:** PLAN-001..PLAN-003, RULE/BIND tasks

- [ ] Implement invocation identity from pack instance, selection, selected semantic identity/scope, template path, and target.
- [ ] Implement stable artifact identity separately from destination path.
- [ ] Include active contexts, target/engine, options, external bindings, generated dependencies, exports, symbols, destination, and lifecycle state.
- [ ] Resolve one target descriptor and one engine per invocation.
- [ ] Support repeated templates, `.all` aggregates, literal templates, static/binary copies, and authored barrel templates.
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

- [ ] Build nodes from registered selection keys and their planned artifact invocations.
- [ ] Resolve explicit `imports: localName: selectionKey` edges.
- [ ] Resolve ordered `exports: [selectionKey]` edges, including barrels exporting barrels.
- [ ] Match consumers/providers by selected semantic identity, active group scope, and explicit symbols.
- [ ] Preserve project-wide, `.all`, `.each`, and active-parent scope.
- [ ] Reject missing providers, ambiguous scopes, duplicate/conflicting symbols, undeclared dependencies, and cycles.
- [ ] Compute deterministic topological order.

## PLAN-007 — Language-neutral dependency and path descriptors

**Status:** planned

**Dependencies:** PLAN-006, target path-validation port

- [ ] Compute the required provider artifacts and symbols for each consumer invocation.
- [ ] Distinguish direct multi-file providers from aggregate and barrel providers.
- [ ] Supply provider/consumer identities, final destinations, relative path segments, target-aware module specifiers, symbols, scope, and local import name.
- [ ] Create immutable ordered export descriptors for authored barrel templates.
- [ ] Allow target adapters only to validate/normalize filename and module/path facts.
- [ ] Prohibit adapters from returning rendered imports, exports, types, literals, comments, validators, decorators, or framework syntax.
- [ ] Keep all emitted text and ordering owned by templates.

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

- [ ] Add exact project/pack commands with executable resolution, opaque arguments, phase, capabilities, and approval state.
- [ ] Do not derive commands from dependency metadata.
- [ ] Add unresolved bindings and manual actions.
- [ ] Compute ready, warning, actions, failed, or cancelled status.

## PLAN-010 — Plan inspection, explain, and serialization

**Status:** planned

**Dependencies:** PLAN-001..PLAN-009, PATH-009

- [ ] Produce stable human and structured plan views.
- [ ] Include source/pack/plugin identities, semantic identities, provenance, selectors/scopes, contexts, templates, expressions, artifacts, destinations, dependency/export graph, symbols, commands, and approvals.
- [ ] Explain every artifact and declared symbol from source semantics through selection/template to destination.
- [ ] Do not promise exact line-level source maps until an engine implements instrumented rendering.
- [ ] Exclude secrets and credentials.
- [ ] Add deterministic snapshots using checked-in examples.

## PLAN-011 — Impact and blast-radius graph

**Status:** planned

**Dependencies:** IR-010, PLAN-004..PLAN-010

- [ ] Relate semantic items/relations to selectors, invocations, provider/consumer artifacts, and barrels.
- [ ] Report semantic causes for create/change/delete/leave decisions.
- [ ] Query all generated artifacts downstream of a schema, operation, view, storage mapping, policy, event, or workflow.
- [ ] Expose stable structured data for CLI, Python API, IDE, and future web visualization.
- [ ] Keep the generation plan as the single source of truth.

## PLAN-012 — Conservative incremental generation

**Status:** planned_after_full_generation

**Dependencies:** deterministic full generation, PLAN-011, ownership/generation state, cache

- [ ] Track semantic, selection, template/include, option/binding, target/engine, and generated-dependency digests.
- [ ] Define conservative context dependency sets and optional safe read tracing.
- [ ] Regenerate broader scope whenever exact impact cannot be proven.
- [ ] Prove incremental output is byte-for-byte equivalent to complete generation.
- [ ] Store output digests/state outside `dryv.lock.yaml`.

## Acceptance gate

- IR contains only closed typed kernel concepts and no OpenAPI, TypeScript, Dart, Jinja, filesystem, command, or CLI classes.
- Adapters and packs cannot extend semantic objects, facets, selectors, or contexts.
- Semantic items expose meaning and names, not generated filenames or syntax.
- Fixed root-first selectors and selection folders plan storage, TypeScript SDK, Flutter, view, workflow, access, and event fixtures.
- Operation inputs/outputs/failures/effects and known facets remain distinct.
- Listener, execution-hook, workflow, and compensation relationships validate by semantic ID.
- Generated dependencies resolve only through declared selection keys, semantic matches, symbols, and planned path facts.
- Templates author every emitted character, including imports/exports and target types.
- Invalid semantic or artifact plans never call renderers or writers.
- Every artifact is explainable and blast-radius queries are deterministic.
