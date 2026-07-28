# Testing, official packs, re-authoring, and release tasks

## TEST-001 — Test architecture

**Status:** planned

**Dependencies:** core package foundation

- [ ] Keep unit tests focused on one rule/class/function where practical.
- [ ] Put reusable adapter behavior in public conformance suites.
- [ ] Keep integration tests as small vertical slices.
- [ ] Add architecture tests for dependency direction, prohibited old imports, closed-kernel ownership, and template-only emitted syntax.
- [ ] Add property tests for identity, naming order, path safety, graph ordering, impact propagation, and cache keys.
- [ ] Add inspectable realistic fixtures rather than only giant snapshots.
- [ ] Prohibit network, shared global registries, environment mutation, and test-order dependence.

## TEST-002 — Configuration fixture matrix

**Status:** planned

**Dependencies:** CFG and PACKCFG tasks

- [ ] Add minimal and complete project fixtures.
- [ ] Add local, Git, mixed, full-project, standalone-folder, and binding-fragment pack fixtures.
- [ ] Add heterogeneous target/engine/static/binary/barrel/partial fixture.
- [ ] Add invalid fixtures for unknown fields, conflicts, unsafe paths, command policy, facet modules, semantic extensions, selector queries, and syntax-rendering adapter rules.
- [ ] Do not add old `tasks` or `paths.yaml` runtime fixtures.

## TEST-003 — Closed-kernel tiny fixture

**Status:** planned

**Dependencies:** IR, planner, fake conforming adapters, memory writer

- [ ] Source contains one group, object schema, enum schema, input use, output use, failure, and operation.
- [ ] Include one view trigger, storage mapping, access policy, event effect/listener, workflow, and optional compensation relation in focused variants.
- [ ] Pack contains TypeScript, YAML, Markdown, static file, neutral partial, and authored barrel templates.
- [ ] Exercise options, bindings, root-first selectors, aggregate template, generated dependency descriptors, and readiness action.
- [ ] Prove all TypeScript/YAML/Markdown text is template-authored.
- [ ] Generate deterministically to memory.

## TEST-004 — Semantic relationship validation fixtures

**Status:** planned

**Dependencies:** IR-010, source adapter conformance

- [ ] Missing schema and operation references.
- [ ] Invalid group ownership and reversed contexts.
- [ ] Invalid storage field/relation targets.
- [ ] Missing policy references and invalid effective access inheritance.
- [ ] Missing event declarations and invalid listener/delivery references.
- [ ] Invalid execution-hook phases, ordering, and bindings.
- [ ] Invalid workflow transitions, waits, branches, and compensation inputs.
- [ ] Unknown facet names and attachment locations.

## TEST-005 — Planning, explain, and impact fixtures

**Status:** planned

**Dependencies:** PLAN-004..PLAN-011

- [ ] Prove stable artifact identity separate from destination.
- [ ] Prove semantic provider matching by group scope and selected identity.
- [ ] Prove artifact/symbol explain traces.
- [ ] Prove schema, operation, storage, view, policy, event, and workflow blast-radius queries.
- [ ] Prove dry-run create/change/delete/leave causes.
- [ ] Prove no renderer runs for invalid semantic or artifact plans.

## TEST-006 — Filesystem and command fixture

**Status:** planned

**Dependencies:** writers, commands, security

- [ ] Generate into a controlled temporary project.
- [ ] Exercise create/change/delete/leave, ownership, protected files, writer rollback, dry run, approved formatter, denied command, and post-commit validation.
- [ ] Verify no mutation on failed/cancelled pre-commit operation.
- [ ] Distinguish writer rollback from workflow compensation in diagnostics and docs.

## PACK-TS — TypeScript SDK pack program

**Status:** planned

**Dependencies:** TypeScript target adapter, Jinja engine, pack planner

- [ ] Complete the aligned package-specific task ledger.
- [ ] Author `DryvPack.yaml` from the v2 schema with group-rooted selectors.
- [ ] Include schema types, enums, operation inputs/outputs/failures, clients, errors, docs/config, authored barrels, static files, bindings, and exact optional commands.
- [ ] Author every type, import, export, comment, literal, and operation statement in templates/macros.
- [ ] Avoid neutral `model`, `resource`, and `entity` contexts.
- [ ] Generate a realistic inspectable SDK and run authored validation commands.

## PACK-DART — Dart SDK pack program

**Status:** planned

**Dependencies:** Dart target adapter, Jinja engine, pack planner

- [ ] Complete the aligned package-specific task ledger.
- [ ] Author standalone or contributed output through project/pack configuration rather than removed profile machinery.
- [ ] Include schema types, enums, operation uses, clients, errors, authored exports, static assets, bindings, and exact optional commands.
- [ ] Author every Dart type/import/export/annotation/serialization statement in templates/macros.
- [ ] Generate a realistic inspectable Dart package and run format/analyze when available.

## PACK-FLUTTER — Flutter integration pack program

**Status:** planned

**Dependencies:** Dart target adapter, Jinja engine, Flutter pack design

- [ ] Keep Flutter as pack/framework policy, not a language-adapter alias.
- [ ] Use `group.views`, view triggers, schemas, operations, access facts, and workflow facts only when present in the kernel input.
- [ ] Author all widget, navigation, state, client, serialization, and validation syntax in templates.
- [ ] Declare project requirements, bindings, assets, manual steps, and exact commands without adding frontend/UI semantic roots.
- [ ] Generate a realistic inspectable Flutter integration fixture.

## PACK-SYSTEM — Connected application-system fixture program

**Status:** planned

**Dependencies:** IR-006..IR-010, PLAN-011, official adapters/engine

- [ ] Build one inspectable contract connecting groups, schemas, operations, views, storage mappings, policies, events, listeners, execution hooks, workflows, and compensation.
- [ ] Generate backend, SDK, mobile/view, storage, workflow, event, and documentation artifacts through separate authored packs.
- [ ] Verify all generated dependencies resolve by semantic identity and declared symbols.
- [ ] Change one schema/operation/policy/event and assert exact blast radius.
- [ ] Prove no source adapter or pack extends the kernel.

## REAUTHOR-001 — Project configuration re-authoring guide

**Status:** planned

**Dependencies:** stable project schema

- [ ] Document how a v1 task becomes a named semantic source plus direct pack instance, output, bindings, options, and commands.
- [ ] Explain command ownership relocation.
- [ ] Remove global language/template-directory assumptions.
- [ ] Provide before/after examples as documentation only.
- [ ] Do not implement a v1 decoder.

## REAUTHOR-002 — Pack re-authoring guide

**Status:** planned

**Dependencies:** stable pack schema and semantic kernel

- [ ] Inventory real old pack needs.
- [ ] Replace `resource`, `model`, `entity`, frontend/UI, and global-first selections with documented group-rooted kernel contexts.
- [ ] Re-author selections, folder fan-out, templates, static files, barrels, imports, bindings, commands, and output paths into v2.
- [ ] Move all type/import/export/framework syntax into templates/macros/partials.
- [ ] Classify intentional semantic/output differences and avoid preserving unsafe implementation quirks.
- [ ] Do not implement a `paths.yaml` parser.

## PERF-001 — Scale and bounds

**Status:** planned

**Dependencies:** functional runtime

- [ ] Test large OpenAPI normalization without repeated parsing or duplicate full semantic graphs.
- [ ] Test large group/schema/operation/view/storage/workflow/event relationship indexes with bounded memory.
- [ ] Test large pack discovery, artifact planning, and impact queries.
- [ ] Test streaming/cache behavior for large artifacts.
- [ ] Test cancellation latency.
- [ ] Publish reproducible fixtures and commands.

## PERF-002 — Incremental equivalence

**Status:** planned_after_full_generation

**Dependencies:** deterministic full generation, PLAN-012, ownership/generation state

- [ ] Compare complete and incremental output byte-for-byte.
- [ ] Test conservative fallback when template context dependencies cannot be proven.
- [ ] Test semantic, template, option, binding, target, engine, and provider changes.
- [ ] Prove no output digest/state is written into `dryv.lock.yaml`.

## SEC-001 — Security review

**Status:** planned

**Dependencies:** adapters, engines, pack providers, commands, writers

- [ ] Review adapter trust messaging and kernel-extension denial.
- [ ] Review Jinja sandbox and immutable context authority.
- [ ] Review Git credential redaction and repository containment.
- [ ] Review command approvals, environment, secrets, shell, network, and lifecycle scripts.
- [ ] Review path traversal, symlink, cleanup, protected files, archive traversal, and cache/state permissions.
- [ ] Add regression tests for every accepted finding.

## REL-001 — Documentation conflict audit

**Status:** planned

- [ ] Verify code implements approved architecture and closed-kernel docs.
- [ ] Search all v2/package docs/tasks/examples for conflicting active uses of `resource`, `model`, `entity`, frontend/UI, reversed selectors, open facets, query DSLs, or adapter-rendered syntax.
- [ ] Treat historical progress/old-runtime docs as evidence only and label them clearly where linked.
- [ ] Verify all public schema/config fields have examples and introspection metadata.
- [ ] Verify package task ledgers match actual versions and tests.
- [ ] Verify progress logs and decisions are complete.

## REL-002 — Package/release matrix

**Status:** planned

**Dependencies:** all official packages

- [ ] Build wheel/sdist for core, bundle, adapters, engine, and packs.
- [ ] Test supported Python versions and operating systems available to the project.
- [ ] Test minimal and batteries-included installs.
- [ ] Test local, public Git, and controlled private Git pack resolution.
- [ ] Test CLI and Python examples from a clean directory.
- [ ] Lock compatible dependency ranges.

## REL-003 — Cutover

**Status:** planned

**Dependencies:** REL-001, REL-002, SEC-001, PERF-001

- [ ] Select final distribution/import namespace cutover.
- [ ] Replace old published runtime with v2 package set.
- [ ] Keep old source as reference/archive without importing it.
- [ ] Publish re-authoring documentation and release notes.
- [ ] Verify default installation lists OpenAPI, TypeScript target validation, Dart target validation, Jinja, and official packs.

## Acceptance gate

Release is blocked unless:

- no v2 code imports the old generator;
- no v2 decoder understands old tasks/paths files;
- the semantic kernel is closed and typed;
- no adapter or pack can add facets/selectors/contexts;
- templates own every emitted character;
- root-first selectors and connected semantic fixtures pass;
- official realistic generated projects validate;
- planning/explain/blast-radius output is deterministic;
- full generation is proven before incremental mode is enabled;
- Python API and CLI use the same services;
- documentation and progress evidence are current.
