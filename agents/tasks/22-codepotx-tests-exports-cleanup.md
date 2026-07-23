# Task 22 — Tests, exports, documentation, and dead-code cleanup

Status: [ ]
Issue: open when ready
Depends on: Task 21
Commit: pending
Validation: pending

## Goal

Mirror the migrated source architecture in tests, curate public exports, remove temporary compatibility shims and dead code, and update documentation to describe the implemented package accurately.

## Test structure

```text
tests/
├── unit/
│   ├── authoring/
│   ├── templating/
│   ├── generation/
│   ├── runtime/
│   └── platform/
├── integration/
├── compatibility/
├── contract/
├── architecture/
└── fixtures/
```

## Test migration

- [ ] Classify every existing test as unit, integration, compatibility, contract, architecture, or fixture support.
- [ ] Move tests in small groups while preserving assertions.
- [ ] Replace the flat `all.test.ts` list with grouped suite entrypoints or native discovery without changing package behavior.
- [ ] Keep real old-contract compatibility fixtures separate from implementation unit tests.
- [ ] Add focused tests for every extracted compiler pass and application use case.
- [ ] Keep filesystem and command integration tests isolated from pure memory tests.
- [ ] Add consumer-package tests for every published subpath.

## Export cleanup

- [ ] Inventory all root and subpath exports after migration.
- [ ] Replace public wildcard exports with explicit curated exports.
- [ ] Preserve supported public symbols and import paths.
- [ ] Mark implementation-only modules as internal by keeping them out of package exports.
- [ ] Remove temporary compatibility re-export files only when no supported consumer depends on them.
- [ ] Verify declaration output contains no private or source-only import paths.

## Code cleanup

- [ ] Remove files made obsolete by completed moves.
- [ ] Remove duplicate helpers, result builders, path functions, and normalization functions only after behavior equivalence is proven.
- [ ] Remove empty folders and one-off barrels that add no boundary value.
- [ ] Remove stale comments and TODOs resolved by the migration.
- [ ] Keep `codepotx-old` and `codepotg` references only as explicit compatibility fixtures or documentation references.
- [ ] Do not remove historical packages as part of this task.

## Documentation

- [ ] Update `packages/nodejs/codepotx/README.md` to describe the actual implementation.
- [ ] Update `agents/ARCHITECTURE.md` to reference the detailed structure guide.
- [ ] Update package subpath documentation.
- [ ] Document the approved internal dependency direction and public/private boundary.
- [ ] Document how to add a compiler pass, template capability, generation stage, runtime operation, and platform adapter.

## Acceptance criteria

- [ ] Test folders mirror stable architecture boundaries.
- [ ] Tests can run by major module and as a complete package suite.
- [ ] Public exports are explicit, documented, and snapshot-tested.
- [ ] No stale implementation files or empty migration scaffolding remain.
- [ ] README status and architecture sections match the code.
- [ ] Package and CLI checks pass.

## Validation

```bash
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
pnpm --filter codepotx package:lint
pnpm --filter codepotx-cli check
```
