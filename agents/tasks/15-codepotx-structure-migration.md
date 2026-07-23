# Task 15 — CodepotX structure migration program

Status: [~]
Issues: #14–#18 closed; #19–#21 open for final combined validation
Depends on: current CodepotX implementation baseline
Commit: implementation proceeds through Tasks 16–23
Validation: Tasks 16–20 passed strict typechecks, 45 CodepotX tests, 3 CLI tests, builds, Publint, and ESM package-resolution checks. Tasks 21–23 are implemented and awaiting the final combined gate.

## Goal

Migrate `packages/nodejs/codepotx` to the structure defined in `agents/CODEPOTX_STRUCTURE_GUIDE.md` without changing public behavior, artifact meaning, authoring inference, template behavior, generation safety, runtime events, or CLI integration.

## Required order

- [x] Task 16 — baseline and architecture guardrails
- [x] Task 17 — contract partitioning and protocol ownership
- [x] Task 18 — authoring compiler and engine modularization
- [x] Task 19 — templating modularization
- [x] Task 20 — generation modularization
- [~] Task 21 — runtime and platform modularization; implementation complete, validation pending
- [~] Task 22 — tests, exports, documentation, and cleanup; implementation complete, validation pending
- [~] Task 23 — full integration and structural migration gate; audit committed, execution pending

## Program rules

- [x] Open one issue per independently reviewable phase when that phase is ready.
- [x] Move code before redesigning behavior.
- [x] Do not hide behavior fixes inside structural commits.
- [x] Preserve package root and subpath exports.
- [x] Preserve strict TypeScript settings.
- [x] Do not introduce `any`, `@ts-ignore`, broad assertions, or disabled checks to complete moves.
- [x] Keep `codepotx` and `codepotx-cli` as the active npm packages.
- [x] Do not add empty folder scaffolding.
- [x] Commit each focused migration unit separately.
- [~] Record final validation evidence and commit SHAs in Tasks 21–23.

## Completion criteria

- [ ] Tasks 16–23 are complete.
- [ ] Every child issue is closed after validation.
- [x] The implemented package follows the approved folder and dependency structure.
- [ ] Public imports and generated behavior match the baseline after the final commits.
- [ ] Workspace and package release checks pass.
