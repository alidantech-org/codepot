# Task 16 — Baseline and architecture guardrails

Status: [~]
Issue: #14
Depends on: Task 15
Commits: `e55a7b58d5705277570a784425e83c7bf7879c8e`, `4c38825c8bdb6d8284152b9e0dca24a0cff22eb1`, `74a9e29e9974894321a9f9aafd95d565ee267869`, `098afba4c23882769324f09582e3eb1566683c3c`, `4838f54b94c204f710eafc49a2fa3b361680fd5d`, `eb3d853d5ff8b0444d9156637f38a38b536eba27`, `07ea66d387e426b139fe68fbab9473305a7122c8`
Validation: guardrails, deterministic baseline, and consumer fixtures committed; local package and CLI execution pending

## Goal

Capture the pre-migration behavior and add automated architecture checks before moving implementation files.

## Baseline

- [x] Record current branch and package version.
- [ ] Run strict package typecheck.
- [ ] Run all CodepotX tests and record test count.
- [ ] Build declarations and JavaScript.
- [ ] Run Publint and Are The Types Wrong.
- [ ] Run external CLI typecheck, tests, build, and package lint.
- [x] Record representative authoring artifact behavior and deterministic JSON-safe output.
- [x] Record representative compiled template-pack behavior and rendered output.
- [x] Record a generation plan and generated file tree.
- [ ] Record managed write, immutable file, stale cleanup, cancellation, and rollback outcomes from the full suite execution.

## Architecture checks

- [x] Add forbidden cross-layer import tests.
- [x] Prevent Node built-in imports from domain layers except explicitly approved runtime infrastructure.
- [x] Prevent imports from `codepotx-old` and Python runtime source.
- [x] Add public root and subpath export snapshots.
- [x] Verify stable artifacts serialize to JSON without functions or implementation instances.
- [x] Verify deterministic artifacts and generation output.
- [x] Detect circular dependency paths across active source layers.
- [x] Verify package subpath imports through a consumer type fixture.

## Type-safety checks

- [x] Add compile-time fixtures for public authoring inference.
- [x] Add an intentional rejection fixture using `@ts-expect-error` only for the expected invalid schema ref.
- [x] Enforce that active source cannot add explicit `any` or `@ts-ignore`.
- [x] Assert strict compiler safeguards remain enabled in `tsconfig.base.json`.

## Acceptance criteria

- [x] Architecture scanner rejects a known forbidden authoring-to-generation import fixture.
- [x] Baseline artifacts and generated files are committed as a stable behavioral fixture.
- [ ] Existing behavior remains unchanged after executing the complete suite.
- [ ] All package and CLI checks pass.

## Validation

Run from the repository root:

```bash
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
pnpm --filter codepotx package:lint
pnpm --filter codepotx-cli check
```

Do not close issue #14 or begin Task 17 until these commands pass and their evidence is recorded.
