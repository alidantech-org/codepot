# Progress log

| Date | Commit | Task | Status | Tests/evidence | Notes |
|---|---|---|---|---|---|
| 2026-07-26 | `763f7128` | Initial scaffold | complete | Documentation and empty directory inspection only; no runtime tests. | Created the first documentation/package skeleton. |
| 2026-07-26 | `12d9b8de` | Adapter package scaffold | complete | File/package inspection only; no runtime tests. | Added OpenAPI, TypeScript, Dart, and Jinja package boundaries. |
| 2026-07-26 | `7f05618f` | Default pack scaffold | complete | File/package inspection only; no runtime tests. | Added TypeScript SDK, Dart SDK, and Flutter SDK package boundaries. |
| 2026-07-26 | `f4c4d3ec` | DOC-001..DOC-006 | complete | Documentation review only; no runtime tests. | Documented the initial v2 architecture and clean-room controls. |
| 2026-07-26 | `0eddff75` | Documentation anti-drift references | complete | Documentation review only; no runtime tests. | Added glossary and linked examples. |
| 2026-07-26 | `8fe8dbdf` | Earlier tokenized path draft | superseded | Documentation review only; no runtime tests. | The `{recipe}` plus `[expression]` and verbose pack sections were replaced by the later approved simplification. |
| 2026-07-26 | `ec2db972` | Approved pack/project simplification | complete | Parsed all seven standalone YAML examples with `yaml.safe_load`; reviewed architecture, project/pack schemas, generation docs, Git/lock docs, and CFG/GIT/PATH tasks. No runtime tests because implementation has not started. | Approved direct `source.local`/`source.git`, fixed selectors, `{selectionKey}`, `{root}`, `(expression)`, `((literal))`, filesystem-discovered files, explicit imports/exports/symbols, exact commands, and `codepotg.lock.yaml`. |
| 2026-07-26 | `446d6965` | Example reconciliation and verification | complete | Re-read mixed project, lock, and TypeScript pack examples from `chatgpt/codepotx-restart`; confirmed the branch head preserved all example files. No runtime tests. | Replaced the concurrently added obsolete `use` sample with the approved direct source/input form. |

## Current stage

The human-oriented project, pack, path, import/export, command, direct Git source, and lock-file contracts are documented and approved. Standalone examples exist for local, Git, mixed, TypeORM, TypeScript SDK, Flutter SDK, and lock configurations.

Runtime implementation has not started.

## Current risks

- Implementation must not restore superseded root `paths`, `files`, `filePatterns`, arbitrary `from`/`as` selections, `registries`, or `use` locators.
- The fixed selector list and generated import/symbol matching must remain versioned and introspectable.
- Exact command arguments must remain opaque to core; package-manager intelligence must not leak into command planning.
- Git credentials must stay outside project/pack/lock files and diagnostics.
- Official pack tasks still contain older wording in package-local ledgers and must be reconciled before those packages are implemented.
- The future `codepotg` import namespace must be cut over in an isolated release environment because old and new distributions cannot own it simultaneously.

## Next action

Before runtime work, reconcile package-local official pack and language-adapter task ledgers with the newly approved central contracts. Then claim the earliest dependency-safe core/configuration task in `PARALLEL_WORK.md`.
