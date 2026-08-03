# Task 20 — Generation modularization

Status: [x]
Issue: #18 closed
Depends on: Task 19 complete
Commits: implementation checkpoint from `8a7daf60d0be9252cc7ac6938f86a15f28f4f955` through `1e6ecde572ce2dde8d435e6467877e537be557d0`; ownership, manifest, and structural follow-ups through `89dcfa5be0e50ee39e424e213d3a37599d86e20f`
Validation: combined Tasks 17–20 gate passed with 45/45 CodepotX tests, strict typechecks, deterministic generation tests, safety and rollback tests, build, Publint, and ESM package checks.

## Goal

Split generation loading, planning, rendering coordination, managed writing, cleanup, manifests, transactions, commands, events, caching, reporting, and task execution into focused modules while preserving deterministic and safe generation behavior.

## Completed structure

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
└── generation-engine.ts
```

## Completion evidence

- [x] `load-codepot-file.ts`, `plan-generation.ts`, `render-generation.ts`, `write-generation.ts`, `clean-generation.ts`, `run-generation-commands.ts`, and `execute-generation.ts` are focused use cases.
- [x] CodepotFile discovery, YAML normalization, `allow: true`, task lookup, and source resolution remain explicit.
- [x] File, command, cleanup, dependency, and complete-plan preparation are separated.
- [x] Rendering depends on the templating port; generation imports no concrete authoring or templating implementation.
- [x] Cache, manifests, stale cleanup, transactions, managed writes, commands, events, and reports have focused ownership.
- [x] Planning completes before writes and dry-run avoids mutations and command execution.
- [x] Managed, immutable, protected, refused, stale cleanup, broad-clean refusal, atomic write, rollback, command ordering, optional commands, and cancellation behavior pass.
- [x] Generation plan, rendered output, manifests, reports, diagnostics, and cache keys remain deterministic and baseline-equivalent.
- [x] Every use case has explicit typed request/result contracts and readonly artifacts are preserved.
- [x] `DefaultGenerationEngine` is a small facade.
- [x] `codepotx/generation` declarations and package resolution pass.

## Validation

```bash
pnpm --filter codepotx check
```
