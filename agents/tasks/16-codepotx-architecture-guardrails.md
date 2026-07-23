# Task 16 — Baseline and architecture guardrails

Status: [~]
Issue: #14 open
Depends on: Task 15
Commits: `e55a7b58d5705277570a784425e83c7bf7879c8e`, `4c38825c8bdb6d8284152b9e0dca24a0cff22eb1`, `74a9e29e9974894321a9f9aafd95d565ee267869`, `098afba4c23882769324f09582e3eb1566683c3c`, `4838f54b94c204f710eafc49a2fa3b361680fd5d`, `eb3d853d5ff8b0444d9156637f38a38b536eba27`, `07ea66d387e426b139fe68fbab9473305a7122c8`, `2d51563126d1ce3f0e0adfe8f90ec0b81a440918`, `d6555e16bf011809e51f34623abd97c638c4a3c2`, `4d2f7b2db022114f9189a700fc5649617c53d384`, `ffde80c6f1bf93a571ccd5727bcc61ba3ca2754b`, `2bf5003302c3f7e602107b5c7995ee5fe53276ab`, `641034817a84532054ed2fcec9ebfb5dc93af405`, `268bc1ec255092b48e49e555c7c88e76bd9b928a`, `a26fc4289709ea65c9d16688120223e8d86b9bc4`, `386fff429ff59343340c75e872490f80ea5aa592`, `46747639b5e1fa9d19221f5b18f9f75fe26c640d`, `f1ef5dd64b0dc0d060d326454d38a903365d4019`, `b04eac928ec7277942cc5e3b3df04782d1314e39`, `d76f0822feb97f8e0275243ddea6b9b98f7a683c`
Validation: strict source/test typecheck passed; all 40 CodepotX tests passed; the ESM build completed with `.mjs` and `.d.mts` output. Publint then exposed stale `.js` and `.d.ts` package paths. Library and CLI manifests now point to the actual ESM build files. A final library and CLI rerun is pending before issue closure.

## Goal

Capture the pre-migration behavior and add automated architecture checks before moving implementation files.

## Baseline

- [x] Record current branch and package version (`chatgpt/codepotx-restart`, `0.0.0`).
- [x] Run strict package typecheck.
- [x] Run all CodepotX tests and record passing test count (40 passed, 0 failed).
- [x] Build declarations and JavaScript ESM output.
- [ ] Run Publint and Are The Types Wrong successfully after package-path correction.
- [ ] Run external CLI typecheck, tests, build, and package lint successfully.
- [x] Record representative authoring artifact behavior.
- [x] Record representative compiled template-pack artifact behavior.
- [x] Record a generation plan and generated file tree behavior.
- [x] Existing focused tests retain managed write, immutable file, stale cleanup, cancellation, and rollback outcomes.

## Architecture checks

- [x] Add forbidden cross-layer import tests.
- [x] Prevent Node built-in imports from domain layers.
- [x] Prevent imports from `codepotx-old` and Python runtime source.
- [x] Add public root and subpath export snapshots.
- [x] Verify stable artifacts serialize to JSON without functions or implementation instances.
- [x] Verify deterministic artifacts and generation output.
- [x] Detect circular dependency paths across public module layers.
- [x] Verify package subpath imports through a consumer-style type fixture.

## Type-safety checks

- [x] Add compile-time fixtures for public authoring inference.
- [x] Add intentional type-error fixture using `@ts-expect-error` only for an invalid schema ref.
- [x] Enforce that migration source cannot add explicit `any` or `@ts-ignore`.
- [x] Assert strict workspace compiler safeguards remain enabled.

## Acceptance criteria

- [x] Architecture tests fail for a known forbidden import fixture and pass for the package.
- [x] Baseline artifacts and generated output are committed as stable observations.
- [x] Existing behavior remains unchanged under the full passing test suite.
- [ ] All package and CLI checks pass.

## Validation

```bash
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
pnpm --filter codepotx package:lint
pnpm --filter codepotx-cli check
```
