# Progress log

| Date | Commit | Task | Status | Tests/evidence | Notes |
|---|---|---|---|---|---|
| 2026-07-26 | `763f7128` | Initial scaffold | complete | Documentation and empty directory inspection only; no runtime tests. | Created the first documentation/package skeleton. |
| 2026-07-26 | `12d9b8de` | Adapter package scaffold | complete | File/package inspection only; no runtime tests. | Added OpenAPI, TypeScript, Dart, and Jinja package boundaries. |
| 2026-07-26 | `7f05618f` | Default pack scaffold | complete | File/package inspection only; no runtime tests. | Added TypeScript SDK, Dart SDK, and Flutter SDK package boundaries. |
| 2026-07-26 | `f4c4d3ec` | DOC-001..DOC-006 | complete | Documentation review only; no runtime tests. | Documented the initial v2 architecture and clean-room controls. |
| 2026-07-26 | `0eddff75` | Documentation anti-drift references | complete | Documentation review only; no runtime tests. | Added glossary and linked examples. |
| 2026-07-26 | `8fe8dbdf` | Earlier tokenized path draft | superseded | Documentation review only; no runtime tests. | The `{recipe}` plus `[expression]` and verbose pack sections were replaced by the later approved simplification. |
| 2026-07-26 | `ec2db972` | Approved pack/project simplification | complete | Parsed all seven standalone YAML examples with `yaml.safe_load`; reviewed architecture, project/pack schemas, generation docs, Git/lock docs, and CFG/GIT/PATH tasks. No runtime tests because implementation had not started. | Approved direct `source.local`/`source.git`, fixed selectors, `{selectionKey}`, `{root}`, `(expression)`, `((literal))`, filesystem-discovered files, explicit imports/exports/symbols, exact commands, and `codepotg.lock.yaml`. |
| 2026-07-26 | `446d6965` | Example reconciliation and verification | complete | Re-read mixed project, lock, and TypeScript pack examples from `chatgpt/codepotx-restart`; confirmed the branch head preserved all example files. No runtime tests. | Replaced the concurrently added obsolete `use` sample with the approved direct source/input form. |
| 2026-07-26 | `e5d23587` | Central and package task alignment | superseded | Reviewed the earlier central/package task ledgers; no runtime tests. | The previous resource/model/entity, global selector, profile, and language-renderer assumptions were replaced by DOC-007. |
| 2026-07-26 | `59f9cb85..b10466d8` | DOC-007 closed semantic kernel alignment | complete | Reviewed and replaced the active governance, foundation, configuration, generation, plugin, distribution/toolchain, rewrite, task, example, OpenAPI, TypeScript/Dart target adapter, and TypeScript/Dart/Flutter pack documents. Updated package progress ledgers. No runtime tests because implementation had not started. | Locked a closed typed kernel, group-rooted selectors, operation inputs/outputs/failures/effects, known facets, views, storage mappings, access, events/listeners, execution hooks, workflows/compensation, template-owned syntax, explain/impact planning, and conservative incremental generation. |
| 2026-07-27 | `bee290cc..be750d1b` | CORE foundation, PATH-001 naming, closed IR, SOURCE/target/engine public ports, fixed selectors | in_progress | Added side-by-side pytest coverage for versions, diagnostics, cancellation/results, exact naming projections, a connected contract with storage/view/event/listener/workflow/compensation, missing-reference validation, fixed selectors, plugin conflicts, source/target/engine conformance, clean-room imports, and isolated wheel build/install. Python/container execution was unavailable in this session and GitHub reported no commit checks, so no test result is claimed yet. | Added installable `codepotg-core`, one unified public diagnostic/version type system, immutable closed semantic objects, validation, root-first selector registry, plugin descriptors, adapter protocols, conformance helpers, `py.typed`, package docs, and released package-local OpenAPI/TypeScript/Dart/Jinja lanes for parallel implementation. |

## Current stage

Actual v2 implementation has started. The public foundation currently includes:

- dependency-free `codepotg-core` package metadata;
- versions, diagnostics, source spans, cancellation, statuses, and operation results;
- deterministic `name.<case>.<number>` projections;
- immutable groups, structural schemas, operations, known facets, views, storage mappings, policies, events/listeners, execution hooks, workflows, and compensation;
- full semantic-reference validation before generation;
- fixed root-first selector contexts;
- public source-adapter, target-adapter, and template-engine protocols;
- plugin descriptors/registry diagnostics and reusable conformance helpers;
- source-tree, connected-contract, architecture, and wheel-install tests.

OpenAPI, TypeScript target, Dart target, and Jinja package-local foundation work may proceed in parallel using only the public contracts listed in `PARALLEL_WORK.md`.

## Current risks

- The new tests must be executed before foundation tasks are marked `review` or `complete`.
- Historical progress rows and old-runtime documents contain superseded vocabulary; they are evidence/reference only and are not active v2 contracts.
- Implementation must not restore root `paths`, explicit `files`, `filePatterns`, profiles, arbitrary selectors, registries/use, or adapter-rendered syntax.
- The closed selector/context list and generated semantic provider matching must remain versioned and introspectable.
- Exact command arguments remain opaque to core; package-manager intelligence must not leak into semantic planning.
- Git credentials remain outside project/pack/lock/state files and diagnostics.
- Output hashes/state remain in ownership/generation state, not `codepotg.lock.yaml`.
- The future `codepotg` namespace cutover must occur in an isolated release environment.

## Next action

Run from `packages/python/codepotg-v2`:

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check src tests
python -m build
```

Repair every failure in the same task slice, then move the core claim to `review`. Parallel package owners may begin only in their own package directories and must not modify claimed core files.
