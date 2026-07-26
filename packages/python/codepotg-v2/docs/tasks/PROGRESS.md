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
| 2026-07-26 | `e5d23587` | Central and package task alignment | superseded | Reviewed the earlier central/package task ledgers; no runtime tests. | The previous resource/model/entity, global selector, profile, and language-renderer assumptions were replaced by DOC-007. |
| 2026-07-26 | `59f9cb85..b10466d8` | DOC-007 closed semantic kernel alignment | complete | Reviewed and replaced the active governance, foundation, configuration, generation, plugin, distribution/toolchain, rewrite, task, example, OpenAPI, TypeScript/Dart target adapter, and TypeScript/Dart/Flutter pack documents. Updated package progress ledgers. No runtime tests because implementation has not started. | Locked a closed typed kernel, group-rooted selectors, operation inputs/outputs/failures/effects, known facets, views, storage mappings, access, events/listeners, execution hooks, workflows/compensation, template-owned syntax, explain/impact planning, and conservative incremental generation. Removed conflicting resource/model/entity/frontend/UI roots, open facets, query DSLs, adapter syntax renderers, profiles, file patterns, and output hashes from the dependency lock. |

## Current stage

The active architecture, configuration, generation, adapter, package, and task documents now share one contract:

- core owns a closed typed semantic kernel;
- adapters and packs cannot extend semantics;
- selectors are fixed, root-first, and outer-to-inner;
- templates/macros/partials/static files own every emitted character;
- target adapters validate targets and calculate path/module facts only;
- OpenAPI and typed `x-codegen` normalize into groups, structural schemas, operations, known facets, views, storage mappings, policies, events, workflows, and compensation;
- plans validate all semantic/artifact relationships before rendering and support explain/blast-radius output;
- deterministic full generation precedes incremental generation.

Runtime implementation has not started.

## Current risks

- Historical progress rows and old-runtime documents contain superseded vocabulary; they are evidence/reference only and are not active v2 contracts.
- Implementation must not restore root `paths`, explicit `files`, `filePatterns`, profiles, arbitrary selectors, registries/use, or adapter-rendered syntax.
- The closed selector/context list and generated semantic provider matching must remain versioned and introspectable.
- Exact command arguments remain opaque to core; package-manager intelligence must not leak into semantic planning.
- Git credentials remain outside project/pack/lock/state files and diagnostics.
- Output hashes/state remain in ownership/generation state, not `codepotg.lock.yaml`.
- The future `codepotg` namespace cutover must occur in an isolated release environment.

## Next action

Claim `CORE-001` on `chatgpt/codepotx-restart` before runtime implementation, then establish packaging/import/version/diagnostic foundations required by the OpenAPI and target adapter packages.
