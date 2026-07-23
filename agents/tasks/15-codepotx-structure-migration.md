# Task 15 — CodepotX structure migration program

Status: [~]
Issues: child issues #14 through #18 currently cover Tasks 16-20
Depends on: current CodepotX implementation baseline
Commit: implementation proceeds through Tasks 16-23
Validation: Task 16 is complete. Tasks 17-20 are implemented and awaiting one combined package validation gate.

## Goal

Migrate `packages/nodejs/codepotx` to the structure defined in `agents/CODEPOTX_STRUCTURE_GUIDE.md` without changing public behavior, artifact meaning, authoring inference, template behavior, generation safety, runtime events, or CLI integration.

This is the umbrella task. Implementation is completed through Tasks 16-23 in order.

## Required order

- [x] Task 16 — baseline and architecture guardrails
- [~] Task 17 — contract partitioning and protocol ownership
- [~] Task 18 — authoring compiler and engine modularization
- [~] Task 19 — templating modularization
- [~] Task 20 — generation modularization
- [ ] Task 21 — runtime and platform modularization
- [ ] Task 22 — tests, exports, documentation, and cleanup
- [ ] Task 23 — full integration and structural migration gate

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
- [~] Record validation evidence and commit SHAs in every child task.

## Completion criteria

- [ ] Tasks 16-23 are complete.
- [ ] Every child issue is closed after validation.
- [ ] The package follows the approved folder and dependency structure.
- [ ] Public imports and generated behavior match the baseline.
- [ ] Workspace and package release checks pass.
