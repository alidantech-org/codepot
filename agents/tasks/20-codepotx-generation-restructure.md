# Task 20 — Generation modularization

Status: [~]
Issue: #18 open
Depends on: Task 19 implementation complete; combined Tasks 17-20 validation pending
Commits: implementation checkpoint from `8a7daf60d0be9252cc7ac6938f86a15f28f4f955` through `1e6ecde572ce2dde8d435e6467877e537be557d0`; ownership, manifest, and structural follow-ups through `89dcfa5be0e50ee39e424e213d3a37599d86e20f`
Validation: all seven application use cases and ownership folders are committed. Safety behavior, baseline equivalence, build, and package compatibility await the combined validation gate.

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

- [x] `load-codepot-file.ts`
- [x] `plan-generation.ts`
- [x] `render-generation.ts`
- [x] `write-generation.ts`
- [x] `clean-generation.ts`
- [x] `run-generation-commands.ts`
- [x] `execute-generation.ts`

## Work

- [x] Separate CodepotFile discovery, YAML parsing, normalization, permission validation, and task lookup behind the loading/config boundary.
- [x] Split file, command, cleanup, and complete-plan preparation into focused planners.
- [x] Extract authoring/template preparation and strict context validation from the main executor.
- [x] Keep rendering delegated through the templating port.
- [x] Group rendered-generation cache logic and keys under `caching/` and `rendering/` ownership.
- [x] Group managed manifest loading, digesting, stale-file detection, and writing under `manifests/`.
- [x] Group transaction capture, completion, rollback, and rollback diagnostics under `transactions/` and execution.
- [x] Group changed-aware write policy and refusal handling under `writing/`.
- [x] Group before/after command planning and execution under `commands/`.
- [x] Group generation event publication under `events/`.
- [x] Group report construction and result aggregation under `reporting/` and execution.
- [x] Adopt `CODEPOT_ARTIFACT_PRODUCER` in generation-plan, rendered-generation, and generation-manifest assembly without changing serialized producer values.
- [x] Make `DefaultGenerationEngine` a small facade over application use cases.

## Safety invariants

- [x] Preserve `allow: true` enforcement in the load use case.
- [x] Preserve complete planning before writes in plan preparation and execution ordering.
- [x] Preserve dry-run propagation without direct mutations or command execution.
- [x] Preserve managed, immutable, protected, and refused file behavior by retaining tested writer/planner components.
- [x] Preserve manifest-based stale cleanup and direct broad-clean refusal.
- [x] Preserve atomic write defaults and rollback behavior.
- [x] Preserve required before/after command ordering and optional command behavior.
- [x] Preserve cancellation checks between stages.
- [ ] Confirm deterministic plans, rendered output, reports, and digests against baseline tests.

## Type-safety requirements

- [x] Give every application use case explicit request/result contracts.
- [x] Keep generation dependent on `AuthoringPort` and `TemplatingPort`, never their concrete implementations.
- [x] Preserve readonly plans and rendered artifacts.
- [x] Remove duplicate result helpers through the typed shared internal result module.
- [x] Add no explicit `any`, `@ts-ignore`, or new unsafe casts.

## Acceptance criteria

- [x] Each generation stage remains independently callable through the engine port with memory adapters.
- [ ] Confirm full execution tests for success, dry run, cancellation, refusal, immutable files, stale cleanup, command failure, and rollback.
- [ ] Baseline plans, files, manifests, and reports remain equivalent.
- [ ] Public `codepotx/generation` exports remain compatible and explicit under package validation.
- [ ] Package checks pass.

## Validation

```bash
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
pnpm --filter codepotx package:lint
```
