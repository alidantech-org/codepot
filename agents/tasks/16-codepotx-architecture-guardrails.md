# Task 16 — Baseline and architecture guardrails

Status: [ ]
Issue: open when ready
Depends on: Task 15
Commit: pending
Validation: pending

## Goal

Capture the pre-migration behavior and add automated architecture checks before moving implementation files.

## Baseline

- [ ] Record current branch and package version.
- [ ] Run strict package typecheck.
- [ ] Run all CodepotX tests and record test count.
- [ ] Build declarations and JavaScript.
- [ ] Run Publint and Are The Types Wrong.
- [ ] Run external CLI typecheck, tests, build, and package lint.
- [ ] Record representative authoring artifact JSON.
- [ ] Record representative compiled template-pack artifact JSON.
- [ ] Record a generation plan, dry-run report, and generated file tree.
- [ ] Record managed write, immutable file, stale cleanup, cancellation, and rollback outcomes.

## Architecture checks

- [ ] Add forbidden cross-layer import tests.
- [ ] Prevent Node built-in imports from domain layers except explicitly approved runtime infrastructure.
- [ ] Prevent imports from `codepotx-old` and Python runtime source.
- [ ] Add public root and subpath export snapshots.
- [ ] Verify stable artifacts serialize to JSON without functions or implementation instances.
- [ ] Verify deterministic artifacts and generation output.
- [ ] Detect circular dependency paths across public module entrypoints.
- [ ] Verify package subpath imports through a consumer fixture.

## Type-safety checks

- [ ] Add compile-time fixtures for public authoring inference.
- [ ] Add intentional type-error fixtures using `@ts-expect-error` only where the rejection is the test.
- [ ] Establish a rule that migration code cannot add `any`, `@ts-ignore`, or disabled strict compiler options.

## Acceptance criteria

- [ ] Architecture tests fail for a known forbidden import fixture and pass for the package.
- [ ] Baseline artifacts and generated files are committed as stable test fixtures or recorded digests.
- [ ] Existing behavior remains unchanged.
- [ ] All package and CLI checks pass.

## Validation

```bash
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
pnpm --filter codepotx package:lint
pnpm --filter codepotx-cli check
```
