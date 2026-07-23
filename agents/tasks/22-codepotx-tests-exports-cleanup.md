# Task 22 — Tests, exports, documentation, and dead-code cleanup

Status: [~]
Issue: #20 open
Depends on: Task 21 implementation complete
Commits: grouped suites from `f03bbeeefcaa03edf111f0d1099f4dc915520202` through `3670341596d6b88e648f9711f297b95e38f64197`; public export curation from `f47569f4ea8185761de89b32c9fa82b0a04421a3` through `dec866535caf745f34b79a33a93db6cb977f3bb9`; consumer/export guardrails `d5cbfdd4424182ae385dc28bd33148221e690b06`, `f3013dd42841779a5d9b87376e334b7494dc0e70`; documentation `0c703f3bee9ceaf9c915d7f674a10c4178296c82`, `708a206e209256fffca59039bdfb15dc9ce8eedc`
Validation: implementation and static guardrails are committed. Strict typecheck, complete behavior suite, declaration build, package validation, and CLI checks remain part of the combined Tasks 21–23 gate.

## Goal

Mirror the migrated source architecture in tests, curate public exports, remove obsolete mixed-ownership implementations, and document the implemented package accurately.

## Test structure

```text
tests/
├── architecture/
├── compatibility/
├── contract/
├── unit/
│   ├── authoring/
│   ├── templating/
│   ├── generation/
│   ├── runtime/
│   └── platform/
├── integration/
└── fixtures/
```

## Test migration completion

- [x] Classify every existing test as architecture, compatibility, contract, unit, integration, or fixture support.
- [x] Preserve every existing assertion and import each original suite exactly once through grouped entrypoints.
- [x] Replace the flat `all.test.ts` list with grouped suite entrypoints.
- [x] Keep old-contract compatibility tests separate from implementation tests.
- [x] Keep compiler, templating, generation, runtime, and platform coverage in focused module groups.
- [x] Keep full runtime/generation/template composition tests under integration.
- [x] Add consumer import fixtures for all seven published package entrypoints.
- [x] Add independent package commands for architecture, compatibility, contract, every unit domain, integration, and the complete suite.

## Export cleanup completion

- [x] Inventory contract exports and review every root/subpath runtime value.
- [x] Replace wildcard exports in all seven published entrypoints with explicit curated exports.
- [x] Preserve supported public symbols and package import paths.
- [x] Keep compiler passes, application use cases, runtime dispatch internals, and platform implementation folders out of package exports.
- [x] Add exact runtime-value snapshots and compile-time consumer fixtures.
- [x] Keep only intentional source-level compatibility shims for migrated flat modules.
- [x] Keep package export keys unchanged.

## Code cleanup completion

- [x] Split the combined source resolver into Node resolver and memory source-store ownership.
- [x] Convert old mixed platform implementations into thin compatibility shims.
- [x] Centralize shared result, path, producer, codec, event, writer, hash, cancellation, clock, and ID ownership where equivalence is proven.
- [x] Retain boundary-value barrels and remove no historical package.
- [x] Keep active source free of imports from `codepotx-old` and `codepotg`.
- [x] Document why compatibility shims remain and forbid new implementation imports through them.

## Documentation completion

- [x] Rewrite `packages/nodejs/codepotx/README.md` for the actual implementation.
- [x] Update `agents/ARCHITECTURE.md` with implemented ownership and dependency direction.
- [x] Document all package subpaths and public/private boundaries.
- [x] Document adding compiler passes, template capabilities, generation stages, runtime operations, and platform adapters.
- [x] Document grouped validation commands and compatibility policy.

## Acceptance criteria

- [x] Test folders mirror stable architecture boundaries.
- [x] Tests can run by major module and as a complete package suite.
- [x] Public exports are explicit, documented, and snapshot-tested.
- [x] No mixed-ownership source resolver or active flat platform implementation remains.
- [x] README status and architecture sections match the code.
- [ ] Confirm declarations contain no private paths and package/CLI checks pass in Task 23.

## Validation

```bash
pnpm --filter codepotx check
pnpm --filter codepotx-cli check
```
