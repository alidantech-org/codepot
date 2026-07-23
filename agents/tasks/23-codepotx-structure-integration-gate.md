# Task 23 — Full structural migration integration gate

Status: [~]
Issue: #21 open
Depends on: Tasks 16–20 complete; Tasks 21–22 implementation complete
Commits: final audit `324004ab4a20edc2a5bb29675d5af7c48d69f285`; integration guardrail `cbe7b62394d186a923a790b0e804ffcf48e318f3`, `bedf0726dc6d67dc4c17868daf93fc52378f3bf1`; grouped architecture wiring `81839d6ba1700ece7fb3f5a0d7602787399f9192`
Validation: static integration gate and final audit are committed. One combined local execution remains required before Tasks 15, 21, 22, and 23 and issues #19–#21 can close.

## Goal

Prove that the completed folder and file migration is behaviorally equivalent, type-safe, package-safe, and ready for continued feature development.

## Structural audit implementation

- [x] Compare the final package tree with `agents/CODEPOTX_STRUCTURE_GUIDE.md` and record it in `agents/audits/CODEPOTX_STRUCTURE_FINAL.md`.
- [x] Add facade-size checks for authoring compiler/engine, templating, generation, runtime, and platform composition.
- [x] Confirm capability folders own implementation and migrated flat platform modules are thin shims.
- [x] Confirm no mixed source-resolver ownership remains.
- [x] Confirm dependency-boundary tests cover contract, internal, authoring, templating, generation, platform, and runtime.
- [x] Confirm public entrypoints contain explicit curated exports and no application/pass/dispatch internals.
- [x] Confirm grouped suites reach every original behavior suite exactly once.
- [x] Confirm documentation and task records are present and current.

## Behavioral equivalence coverage

- [x] Authoring artifacts are compared with the Task 16 baseline.
- [x] Compiled template packs are compared with baseline fixtures.
- [x] Template context, variable catalogs, strict validation, and rendered files are covered.
- [x] Generation plans, files, manifests, cache keys, reports, and diagnostics are covered.
- [x] Managed, immutable, protected, cleanup, command, transaction, rollback, dry-run, cancellation, cache, and event behavior are covered.
- [x] Real old-style TypeScript compatibility contracts are included.
- [x] Shared Python-compatible template context behavior is covered where intentionally ported.
- [x] CLI request mapping and frontend-only presentation remain covered by CLI tests.

## Type and package validation implementation

- [x] Public generic inference and every package subpath are imported by `tests/public-entrypoints.fixture.ts`.
- [x] Runtime value surfaces are snapshot-tested.
- [x] Public package keys remain unchanged.
- [x] Public wildcard exports are rejected.
- [x] Runtime operation registration is exhaustive and cast-free at the dispatch boundary.
- [x] Node and memory adapter parity remains in the complete suite.
- [ ] Strict source/test typecheck and declaration generation must pass after all final commits.
- [ ] Publint and Are The Types Wrong must pass for CodepotX and CLI.
- [ ] Workspace check and build must pass.

## Full validation

```bash
pnpm --filter codepotx check
pnpm --filter codepotx-cli check
pnpm check
pnpm build
```

The package suite includes dry-run and temporary real-write generation behavior through memory and temporary Node adapters.

## Completion criteria

- [ ] Tasks 16–22 are complete with closed issues and validation evidence.
- [ ] All commands and behavioral comparisons pass.
- [x] Final package tree and compatibility-shim policy are documented.
- [x] No unresolved migration exception remains.
- [ ] Task 15 is marked complete after the final gate.
- [ ] Issue #21 closes only after the final validation evidence is committed.
