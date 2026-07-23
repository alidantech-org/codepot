# Task 23 — Full structural migration integration gate

Status: [ ]
Issue: open when ready
Depends on: Tasks 16-22
Commit: pending
Validation: pending

## Goal

Prove that the completed folder and file migration is behaviorally equivalent, type-safe, package-safe, and ready for continued feature development.

## Structural audit

- [ ] Compare the final package tree with `agents/CODEPOTX_STRUCTURE_GUIDE.md`.
- [ ] Confirm no oversized multi-responsibility orchestration module remains without an explicit exception.
- [ ] Confirm folders group capabilities instead of accumulating unrelated flat files.
- [ ] Confirm no empty scaffolding folders remain.
- [ ] Confirm dependency-boundary tests cover every active layer.
- [ ] Confirm public exports contain no accidental internals.

## Behavioral equivalence

- [ ] Compare authoring artifacts with baseline fixtures.
- [ ] Compare compiled template-pack artifacts with baseline fixtures.
- [ ] Compare template variable catalogs and strict context validation.
- [ ] Compare generation plans, rendered files, manifests, reports, and diagnostics.
- [ ] Verify managed, immutable, protected, cleanup, command, transaction, rollback, dry-run, cancellation, cache, and event behavior.
- [ ] Run real old TypeScript compatibility contracts.
- [ ] Run representative CodepotG parity fixtures where behavior is intentionally shared.
- [ ] Verify external CLI requests and presentation remain compatible.

## Type and package validation

- [ ] Strict source and test typecheck pass without new suppressions.
- [ ] Public generic inference fixtures pass.
- [ ] Declaration generation succeeds.
- [ ] Root and subpath consumer fixtures compile and execute.
- [ ] Publint passes.
- [ ] Are The Types Wrong passes with the ESM-only profile.
- [ ] Package contents contain only intended runtime files, declarations, README, license, and metadata.

## Full validation

```bash
pnpm --filter codepotx check
pnpm --filter codepotx-cli check
pnpm check
pnpm build
```

Also run the recorded generation fixture workflow in both dry-run and temporary real-write modes.

## Completion criteria

- [ ] Tasks 16-22 are marked complete with closed issues and validation evidence.
- [ ] All commands and behavioral comparisons pass.
- [ ] Final package tree is documented.
- [ ] Migration exceptions, if any, have explicit reasons and follow-up tasks.
- [ ] Task 15 is updated as complete.
- [ ] The integration issue is closed only after the final validation commit is on the active branch.
