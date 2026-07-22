# Phase 06 — External CLI frontend

Status: [ ]
Issue: open when runtime generation is stable
Depends on: Phases 01-05
Commit: pending
Validation: pending

## Goal

Create `packages/nodejs/codepotx-cli` as a thin frontend over `codepotx/runtime` and `codepotx/contract`.

## 06.1 Package and contracts

- [ ] Add the CLI workspace package without moving domain logic into it.
- [ ] Depend on a compatible local/published `codepotx` version.
- [ ] Define CLI command input and presentation interfaces before implementation.
- [ ] Expose the `codepotx` executable from the CLI package.

## 06.2 Commands

- [ ] Map authoring validate/inspect/compile commands to runtime requests.
- [ ] Map template validate/inspect commands to runtime requests.
- [ ] Map generation plan/run/dry-run/refresh commands to runtime requests.
- [ ] Support task selection, all tasks, explicit config paths, verbosity, and cancellation.
- [ ] Keep prompts and confirmation only in the CLI frontend.

## 06.3 Presentation

- [ ] Render typed diagnostics consistently.
- [ ] Render progress and lifecycle events without blocking domain execution.
- [ ] Render concise summaries for planned, created, updated, unchanged, skipped, immutable, refused, cleaned, and command results.
- [ ] Map structured outcomes to stable exit codes.
- [ ] Avoid direct filesystem, YAML, TypeScript loading, template rendering, generation planning, or writing in CLI code.

## 06.4 Validation

- [ ] Test commands using an injected runtime test harness.
- [ ] Verify CLI and direct runtime calls return equivalent domain results.
- [ ] Verify listener/presentation failures do not alter runtime results.
- [ ] Verify local package execution and globally installed delegation strategy.
- [ ] Typecheck, tests, build, package validation, and packed CLI smoke tests pass.
- [ ] Record issue, commit, and evidence before marking complete.
