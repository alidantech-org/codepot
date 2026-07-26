# Testing, official packs, re-authoring, and release tasks

## TEST-001 — Test architecture

**Status:** planned

**Dependencies:** CORE package foundation

- [ ] Keep unit tests focused on one rule/class/function where practical.
- [ ] Put reusable plugin behavior in contract suites.
- [ ] Keep integration tests as small vertical slices.
- [ ] Add architecture tests for dependency direction and prohibited old imports.
- [ ] Add property tests for rule merging, path safety, graph ordering, and cache keys.
- [ ] Add inspectable realistic fixtures rather than only giant snapshots.
- [ ] Prohibit network, shared global registries, environment mutation, and test-order dependence.

## TEST-002 — Configuration fixture matrix

**Status:** planned

**Dependencies:** CFG and PACKCFG tasks

- [ ] Add minimal and complete `Project` fixtures.
- [ ] Add full-project, standalone-folder, dependency-extension, and binding-fragment pack fixtures.
- [ ] Add heterogeneous target/engine/static/binary/barrel/partial fixture.
- [ ] Add invalid fixtures for every unknown field, conflict, unsafe path, override denial, and command policy.
- [ ] Do not add old `tasks` or `paths.yaml` runtime fixtures.

## TEST-003 — End-to-end tiny fixture

**Status:** planned

**Dependencies:** IR, planner, fake conforming adapters, memory writer

- [ ] Source contains one model, enum, request, response, and operation.
- [ ] Pack contains TypeScript template, YAML template, Markdown template, static `.gitignore`, neutral partial, and authored barrel.
- [ ] Exercise option, binding, default barrel, aggregate template, and readiness action.
- [ ] Generate deterministically to memory.

## TEST-004 — Filesystem and command fixture

**Status:** planned

**Dependencies:** writers, commands, security

- [ ] Generate into a controlled temporary project.
- [ ] Exercise create/change/delete/leave, ownership, protected file, rollback, dry run, approved staged formatter, denied command, and post-commit validation.
- [ ] Verify no mutation on failed/cancelled pre-commit operation.

## PACK-TS — TypeScript SDK pack program

**Status:** planned

**Dependencies:** TypeScript adapter, Jinja engine, pack planner

- [ ] Complete package-specific task ledger.
- [ ] Author `CodepotgPack.yaml` from the v2 schema.
- [ ] Include modular and monolithic profiles.
- [ ] Include models, enums, DTOs, operations/client, errors, docs/config, authored barrels, static files, bindings, Node dependencies, setup, and optional polish actions.
- [ ] Validate npm/pnpm/Yarn portability.
- [ ] Generate realistic inspectable SDK and run declared validation.

## PACK-DART — Dart SDK pack program

**Status:** planned

**Dependencies:** Dart adapter, Jinja engine, pack planner, Dart ecosystem

- [ ] Complete package-specific task ledger.
- [ ] Author standalone package output with owned `pubspec.yaml` where configured.
- [ ] Include modular and monolithic options as appropriate, authored barrels/exports, static package assets, dependency declarations, package-name binding, setup actions, and docs.
- [ ] Validate package imports and relative imports.
- [ ] Generate realistic inspectable Dart package and run format/analyze when available.

## PACK-FLUTTER — Flutter SDK/integration pack program

**Status:** planned

**Dependencies:** Dart pack/adapters, Flutter-specific pack design

- [ ] Keep Flutter as pack/framework policy, not a language adapter alias.
- [ ] Declare host Flutter/pubspec requirements, dependencies, assets, bindings, manual steps, and build-runner actions.
- [ ] Support standalone generated package or existing-app contribution according to pack profile.
- [ ] Generate realistic inspectable Flutter integration fixture.

## REAUTHOR-001 — Project configuration re-authoring guide

**Status:** planned

**Dependencies:** stable project schema

- [ ] Document how a v1 task is conceptually re-authored as named source + pack instance + output/bindings/options/commands.
- [ ] Explain command ownership relocation.
- [ ] Remove global language and template directory assumptions.
- [ ] Provide before/after examples as documentation only.
- [ ] Do not implement a v1 decoder in runtime.

## REAUTHOR-002 — Pack re-authoring guide

**Status:** planned

**Dependencies:** stable pack schema

- [ ] Inventory real old pack needs.
- [ ] Re-author selections, folder fan-out, templates, static files, authored barrels, imports, bindings, dependencies, setup, commands, and write policy into v2 manifest.
- [ ] Explain how old folder concepts become `filePatterns` and one-file descriptors.
- [ ] Classify output differences and avoid preserving unsafe implementation quirks.
- [ ] Do not implement a `paths.yaml` parser in v2.

## PERF-001 — Scale and bounds

**Status:** planned

**Dependencies:** functional runtime

- [ ] Test large OpenAPI normalization without repeated parsing or duplicate full graphs.
- [ ] Test large file discovery and plan graphs with bounded memory.
- [ ] Test streaming/cache behavior for large artifacts.
- [ ] Test cancellation latency.
- [ ] Publish reproducible benchmark fixtures and commands.

## SEC-001 — Security review

**Status:** planned

**Dependencies:** plugins, engines, pack providers, commands, writers

- [ ] Review Python plugin trust messaging.
- [ ] Review Jinja sandbox and context authority.
- [ ] Review Git credential redaction and repository containment.
- [ ] Review command approvals, environment, secrets, shell, network, and lifecycle scripts.
- [ ] Review path traversal, symlink, cleanup, protected files, archive traversal, and cache permissions.
- [ ] Add regression tests for every accepted finding.

## REL-001 — Documentation audit

**Status:** planned

- [ ] Verify code implements approved docs.
- [ ] Verify no task/document requests compatibility runtime.
- [ ] Verify all public schema fields have examples and introspection metadata.
- [ ] Verify plugin and package task ledgers match actual versions and tests.
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
- [ ] Keep old source as reference/archive according to repository decision, without importing it.
- [ ] Publish re-authoring documentation and release notes.
- [ ] Verify default installation lists OpenAPI, TypeScript, Dart, Jinja, and official packs.

## Acceptance gate

Release is blocked unless:

- no v2 code imports the old generator;
- no v2 config decoder understands old tasks/paths files;
- all architecture/conformance/security suites pass;
- official realistic generated projects validate;
- Python API and CLI use the same application services;
- batteries-included installation works from a clean environment;
- documentation and progress evidence are current.
