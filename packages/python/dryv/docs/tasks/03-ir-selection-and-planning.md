# Closed IR, selection, and planning tasks

All work in this ledger preserves one closed typed Dryv kernel. No task may add provider-defined semantic objects, generic fact bags, arbitrary traversal selectors, or adapter-rendered target syntax.

## IR-001 — Provenance and semantic identity

- [x] Source-neutral contract and semantic identities.
- [x] Source spans without provider-specific runtime objects.
- [x] Deterministic equality, hashing, and ordering.
- [ ] Improve explicit rename provenance without guessing delete-plus-add changes.

## IR-002 — Names, types, and schemas

- [x] `name.<case>.<number>` projections.
- [x] Structural schema kinds and neutral type expressions.
- [x] Fields, constraints, references, and optional-versus-nullable semantics.
- [x] No target-language or framework schema kinds.
- [ ] Publish concise API reference and cookbook recipes.

## IR-003 — Groups and semantic relationships

- [x] Group containment and stable ownership.
- [x] Schemas, operations, views, storage, workflows, policies, events, value sources, presentations, guidance, tags, and known facets.
- [x] Immutable schema-use and cross-reference records.
- [ ] Expand validation fixtures for deeply connected real projects.

## IR-004 — Validation and private indexes

- [x] Uniform deterministic diagnostics.
- [x] Typed internal indexes for semantic ownership and references.
- [x] Missing, conflicting, invalid, and cyclic relationship checks.
- [x] Private graph implementation with typed public/template APIs.
- [ ] Add richer related-location diagnostics.

## PLAN-001 — Pack discovery

- [x] Deterministic traversal of `templates/`.
- [x] Pack-root ignore rules and include/exclude handling.
- [x] Partials, templates, static text, binary files, and documentation classification.
- [x] Engine/target suffix inference and path containment.
- [ ] Expand symlink and platform-specific collision fixtures.

## PLAN-002 — Fixed selectors

- [x] Versioned core-owned selector registry.
- [x] `.each` and supported aggregate cardinalities.
- [x] Stable outer-to-inner contexts.
- [x] Zero selected contexts produce zero artifacts.
- [ ] Add new selectors only after a repeated pack need justifies a typed behavior-versioned change.

Current registry:

```text
groups.all
groups.each
groups.schemas.each
groups.schemas.objects.each
groups.schemas.enums.each
groups.operations.each
groups.views.each
groups.storage.mappings.each
groups.workflows.each
groups.policies.each
groups.events.each
groups.value_sources.each
presentations.each
presentations.entries.each
```

## PLAN-003 — Selection-folder expansion

- [x] Whole `{selectionKey}` path segments.
- [x] Registered selection paths relative to pack output roots.
- [x] Left-to-right nested expansion.
- [x] Consistent fan-out for templates, static files, and binary files.
- [x] Missing-key, shadowing, cycle, and duplicate-invocation diagnostics.

## PLAN-004 — Artifact identity

- [x] Stable invocation and artifact identity separate from destination path.
- [x] Pack, selection, semantic, template, target, option, binding, and dependency causes.
- [x] Repeated templates, aggregate templates, literal templates, static/binary files, and authored barrels.
- [ ] Expose full identity details through the public runtime inspection API.

## PLAN-005 — Partials and template dependencies

- [x] Declared `_partials` registry.
- [x] No undeclared filesystem includes.
- [x] Cycle and depth protection through the engine contract.
- [ ] Add serializable template/partial edges to impact analysis.

## PLAN-006 — Generated dependencies and symbols

- [x] Explicit imports and exports between selections.
- [x] Semantic-ID, group-scope, and selection fallback matching.
- [x] Declared symbol providers.
- [x] Target-aware module/path facts.
- [x] Deterministic dependency order.
- [ ] Improve ambiguous-provider diagnostics and provider selection explanations.

Target adapters may validate and normalize path facts only. Templates own every emitted import, export, type, literal, comment, validator, decorator, and framework statement.

## PLAN-007 — Output and collision graph

- [x] Safe literal and expression destinations.
- [x] Engine suffix stripping with target suffix preservation.
- [x] Pack output-root composition.
- [x] Traversal, absolute path, invalid segment, symlink escape, target filename, and duplicate-destination checks.
- [x] Invalid plans never call a renderer or writer.

## PLAN-008 — Commands and readiness

- [x] Command declarations are preserved and fail closed while the command runtime is unavailable.
- [ ] Add exact executable, argument, provenance, phase, capability, and approval records.
- [ ] Keep package-manager syntax opaque and project/pack authored.

## PLAN-009 — Plan inspection

- [x] Deterministic plan and artifact summaries.
- [x] Artifact cause, template, selection, semantic ID, target, symbols, imports, and exports.
- [ ] Publish stable runtime lookup by artifact ID and path.
- [ ] Add complete semantic-to-artifact explanation.
- [ ] Exclude secrets and credentials from every result.

## PLAN-010 — Impact graph

- [ ] Relate semantic objects to selectors and artifacts.
- [ ] Add generated provider, export, template, partial, config, and pack edges.
- [ ] Report semantic causes for create/change/delete/leave decisions.
- [ ] Publish serializable data for CLI, IDE, server, and MCP hosts.

## PLAN-011 — Conservative incremental generation

- [ ] Begin only after deterministic full generation and impact analysis are proven.
- [ ] Regenerate broader scope whenever exact impact cannot be established.
- [ ] Prove incremental output equals a fresh complete generation byte-for-byte.
- [ ] Keep generated output digests in ownership state, not `dryv.lock.yaml`.

## Acceptance gate

- IR contains only closed typed Dryv concepts and no provider, target, template-engine, filesystem, command, or UI implementation classes.
- Packs and plugins cannot extend semantic meaning.
- Selectors are core-owned and behavior-versioned.
- Every artifact is fully planned and explainable before rendering.
- Invalid plans cause no rendering or filesystem mutation.
- Templates remain the exclusive owners of emitted target text.
