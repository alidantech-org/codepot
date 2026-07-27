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
| 2026-07-27 | `bee290cc..be750d1b` | First CORE/PATH/IR/port implementation | superseded | Initial side-by-side pytest files were added, but the implementation was incorrectly concentrated in flat modules and was not executed before the checkpoint was reported. | Replaced by the organized corrective implementation below. This row remains as evidence of the rejected structure. |
| 2026-07-27 | user verification of `537d4740` | Package/test/lint verification | failed | `pytest`: 25 passed, 1 failed. Editable install and `python -m build` failed because `license = "MIT"` was combined with the superseded MIT license classifier. Ruff reported 20 findings: import organization, `StrEnum` modernization, and `collections.abc` imports. | The logs proved the checkpoint was not release-ready and triggered the structural correction. |
| 2026-07-27 | `8fe22aa3..96153b3f` | Organized CORE/PATH/IR/ports correction | in_progress | Removed the conflicting license classifier; reorganized source into `api`, `application`, `config`, `domain/ir`, `domain/generation`, `plugins`, `ports`, `runtime`, `infrastructure`, and `cli`; mirrored tests under unit/contracts/architecture/distribution/fixtures; removed flat module/package collisions; replaced string enums with `StrEnum`; corrected collection imports and reported import-order findings. Full command rerun remains required. | Architecture tests now explicitly reject flat source/test dumps and same-name module/package collisions. Validation was separated into semantic indexing and reference validation. No passing result is claimed yet for the reorganized tree. |

## Current stage

Actual v2 implementation has started, and the first foundation is being corrected and verified. The source now follows the approved package boundaries, while tests mirror those boundaries instead of living as root-level files.

Implemented foundation areas:

- dependency-free `codepotg-core` package metadata;
- versions, diagnostics, source spans, cancellation, statuses, and operation results;
- deterministic `name.<case>.<number>` projections;
- immutable groups, structural schemas, operations, known facets, views, storage mappings, policies, events/listeners, execution hooks, workflows, and compensation;
- semantic identity indexing and cross-reference validation before generation;
- fixed root-first selector contexts;
- public source-adapter, target-adapter, and template-engine protocols;
- plugin descriptors/registry diagnostics and reusable conformance helpers;
- organized unit, contract, architecture, fixture, and isolated-wheel tests.

OpenAPI, TypeScript target, Dart target, and Jinja package-local foundation work may proceed only through the published public namespaces and must not import `codepotg.domain` implementation modules.

## Current risks

- The reorganized test suite and package build must be executed before foundation tasks move to `review` or `complete`.
- Historical progress rows and old-runtime documents contain superseded vocabulary; they are evidence/reference only and are not active v2 contracts.
- Implementation must not restore flat source/test dumps, root `paths`, explicit `files`, `filePatterns`, profiles, arbitrary selectors, registries/use, or adapter-rendered syntax.
- Public facades must remain explicit; no same-name module/package collision may return.
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

Repair every remaining failure in the same task slice. Only then move the core claim to `review` and publish a stable foundation commit for the parallel packages.
