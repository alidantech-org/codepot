# Task 15 — CodepotX structure migration program

Status: [ ]
Issue: open only when the first migration phase is ready
Depends on: current CodepotX implementation baseline
Commit: pending
Validation: pending

## Goal

Migrate `packages/nodejs/codepotx` to the structure defined in `agents/CODEPOTX_STRUCTURE_GUIDE.md` without changing public behavior, artifact meaning, authoring inference, template behavior, generation safety, runtime events, or CLI integration.

This is the umbrella task. Implementation is completed through Tasks 16-23 in order.

## Required order

- [ ] Task 16 — baseline and architecture guardrails
- [ ] Task 17 — contract partitioning and protocol ownership
- [ ] Task 18 — authoring compiler and engine modularization
- [ ] Task 19 — templating modularization
- [ ] Task 20 — generation modularization
- [ ] Task 21 — runtime and platform modularization
- [ ] Task 22 — tests, exports, documentation, and dead-code cleanup
- [ ] Task 23 — full integration and structural migration gate

## Program rules

- [ ] Open one issue per independently reviewable phase.
- [ ] Move code before redesigning behavior.
- [ ] Do not hide behavior fixes inside structural commits.
- [ ] Preserve package root and subpath exports.
- [ ] Preserve strict TypeScript settings.
- [ ] Do not introduce `any`, `@ts-ignore`, broad assertions, or disabled checks to complete moves.
- [ ] Keep `codepotx` and `codepotx-cli` as the active npm packages.
- [ ] Do not add empty folder scaffolding.
- [ ] Commit each focused migration unit separately.
- [ ] Record validation evidence and commit SHAs in every child task.

## Completion criteria

- [ ] Tasks 16-23 are complete.
- [ ] Every child issue is closed after validation.
- [ ] The package follows the approved folder and dependency structure.
- [ ] Public imports and generated behavior match the baseline.
- [ ] Workspace and package release checks pass.
