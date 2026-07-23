# Task 20 — Generation modularization

Status: [ ]
Issue: open when ready
Depends on: Task 19
Commit: pending
Validation: pending

## Goal

Split generation loading, planning, rendering coordination, managed writing, cleanup, manifests, transactions, commands, events, caching, reporting, and full task execution into focused modules while preserving deterministic and safe generation behavior.

## Target structure

```text
src/generation/
├── config/
├── planning/
├── rendering/
├── writing/
├── manifests/
├── transactions/
├── commands/
├── caching/
├── reporting/
├── events/
├── application/
└── index.ts
```

## Application use cases

- [ ] `load-codepot-file.ts`
- [ ] `plan-generation.ts`
- [ ] `render-generation.ts`
- [ ] `write-generation.ts`
- [ ] `clean-generation.ts`
- [ ] `run-generation-commands.ts`
- [ ] `execute-generation.ts`

## Work

- [ ] Separate CodepotFile discovery, YAML parsing, normalization, permission validation, and task lookup.
- [ ] Split file, command, and cleanup planning into focused planners.
- [ ] Extract authoring/template preparation and strict context validation from the main executor.
- [ ] Keep rendering delegated through the templating port.
- [ ] Group rendered-generation cache logic and keys.
- [ ] Group managed manifest loading, digesting, stale-file detection, and writing.
- [ ] Group transaction capture, completion, rollback, and rollback diagnostics.
- [ ] Group changed-aware write policy and refusal handling.
- [ ] Group before/after command planning and execution.
- [ ] Group generation event publication.
- [ ] Group report construction and result aggregation.
- [ ] Adopt `CODEPOT_ARTIFACT_PRODUCER` from `src/internal/package-info.ts` in generation-plan, rendered-generation, and generation-manifest assembly without changing serialized producer values.
- [ ] Make `DefaultGenerationEngine` a small facade over application use cases.

## Safety invariants

- [ ] Preserve `allow: true` enforcement.
- [ ] Preserve complete planning before writes.
- [ ] Preserve dry-run behavior without mutations or command execution.
- [ ] Preserve managed, immutable, protected, and refused file behavior.
- [ ] Preserve manifest-based stale cleanup and broad-clean refusal.
- [ ] Preserve atomic write defaults and rollback behavior.
- [ ] Preserve required before/after command ordering and optional command behavior.
- [ ] Preserve cancellation checks between stages.
- [ ] Preserve deterministic plans, rendered output, reports, and digests.

## Type-safety requirements

- [ ] Give every application use case explicit request/result contracts.
- [ ] Keep generation dependent on `AuthoringPort` and `TemplatingPort`, never their concrete implementations.
- [ ] Preserve readonly plans and rendered artifacts.
- [ ] Remove duplicate result helpers only through typed shared internal modules.
- [ ] Add no unsafe casts or type suppressions.

## Acceptance criteria

- [ ] Each generation stage can be tested independently with memory adapters.
- [ ] Full execution tests cover success, dry run, cancellation, refusal, immutable files, stale cleanup, command failure, and rollback.
- [ ] Baseline plans, files, manifests, and reports remain equivalent.
- [ ] Public `codepotx/generation` exports remain compatible and explicit.
- [ ] Package checks pass.

## Validation

```bash
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
pnpm --filter codepotx package:lint
```
