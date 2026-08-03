# Phase 07 — Integration, parity, packaging, and release

Status: [ ]
Issue: open when Phases 01-06 are complete
Depends on: Phases 01-06
Commit: pending
Validation: pending

## Goal

Prove the complete restart is compatible, deterministic, decoupled, publishable, and smooth for real consumers.

## 07.1 End-to-end compatibility

- [ ] Run old authoring fixtures with import-only migration.
- [ ] Compare stable authoring artifacts against approved expectations.
- [ ] Compare converted Python template fixtures, path plans, context, dependencies, imports, and generated files.
- [ ] Compare CodepotFile task selection, commands, cleanup, writing classifications, dry runs, diagnostics, and events.
- [ ] Verify fresh source, cached artifact, and precompiled artifact modes produce equivalent generation.

## 07.2 Architecture validation

- [ ] Verify dependency direction and forbidden imports.
- [ ] Verify all cross-layer interactions use shared ports.
- [ ] Verify runtime is the only composition root.
- [ ] Verify the CLI has no domain logic.
- [ ] Verify events are observational and listener failures are isolated.
- [ ] Verify domain tests run with in-memory adapters.

## 07.3 Consumer fixtures

- [ ] ESM consumer with no custom `tsconfig.json`.
- [ ] Consumer using `moduleResolution: bundler`.
- [ ] Consumer using `@/*` aliases.
- [ ] pnpm workspace/monorepo consumer.
- [ ] Windows path fixture.
- [ ] local, package, Git, and compiled-artifact sources.
- [ ] packed `codepotx` and `codepotx-cli` installation fixture.

## 07.4 Package and release validation

- [ ] Generate and commit `pnpm-lock.yaml`.
- [ ] Run typecheck, tests, build, and Turbo checks.
- [ ] Run Publint and Are The Types Wrong on packed artifacts.
- [ ] Inspect tarball contents and public exports.
- [ ] Verify no internal aliases, source files, secrets, caches, or unintended deep imports leak into packages.
- [ ] Produce migration and release notes.

## Completion

- [ ] Every completed task issue is closed.
- [ ] No task is marked complete without evidence and commit SHA.
- [ ] Remaining open issues represent only genuinely incomplete work.
- [ ] Final release candidate is reviewed against all agent rules and feature requirements.
