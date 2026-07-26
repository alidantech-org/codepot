# Parallel work registry

This file coordinates implementation across conversations. Claim a task before changing implementation files.

## Active claims

| Task ID | Package/subsystem | Owner/chat | Status | Expected files | Dependencies | Notes |
|---|---|---|---|---|---|---|
| CORE-001..CORE-006, PATH-001, IR-001..IR-010, SOURCE-001, PLUG-001 public contracts | `codepotg-v2` foundation, closed IR, and adapter ports | current ChatGPT implementation session | in_progress | `pyproject.toml`, public `src/codepotg/**` primitives/IR/plugin/port/testing modules, focused unit/contract/architecture tests, task/progress evidence | DOC-001..DOC-007 | Establish the smallest tested public foundation required for OpenAPI, TypeScript, Dart, and Jinja packages to proceed independently. No planner, writer, CLI, or compatibility runtime is included. |

## Planned task lanes

| Lane | Task range | Primary ownership | May start when |
|---|---|---|---|
| Core primitives | CORE-001..CORE-006 | `codepotg-v2` | documentation accepted |
| Semantic naming/expressions | PATH-001..PATH-003 | core naming/path contracts | core version and diagnostics available |
| Configuration | CFG-001..CFG-006, PACKCFG-001..PACKCFG-005 | `codepotg-v2/config` | core diagnostics available |
| Closed semantic kernel | IR-001..IR-010 | domain/IR and validators | core primitives and PATH-001 stable |
| Root-first selectors/selection folders | PLAN-002..PLAN-004, PATH-004, PATH-006 | generation/config/IR contracts | typed config and kernel stable |
| Filesystem discovery/path planning | PLAN-001, PLAN-003..PLAN-010, PATH-005, PATH-007..PATH-010 | generation domain/application | pack config, expressions, selectors, and IR stable |
| Generated dependencies/path facts | BIND-002, PLAN-006..PLAN-007, PATH-008 | semantic artifact graph + target path ports | selections, artifacts, destinations, and symbols stable |
| Explain and impact | PLAN-010..PLAN-011 | planner/inspection API | semantic and artifact plans stable |
| Conservative incremental generation | PLAN-012 | planner/cache/state | deterministic full generation and impact graph proven |
| Plugin runtime | PLUG-001..PLUG-011 | plugins/ports/runtime | public primitives and closed-kernel boundary stable |
| Writers/cache/state | WRITE/CACHE tasks | infrastructure + ports | artifact/path plan stable |
| Commands/setup | CFG-004..CFG-005, CMD, SETUP/CONFIGURE/ECO | application/infrastructure | config/security contracts stable |
| Python API/CLI | API/CLI/MCP and impact API | api/application/cli | core use cases stable |
| Local/Git distribution | GIT/LOCK/DIST | pack provider/lock/cache | direct source and pack manifest contracts stable |
| OpenAPI adapter | OA-001..OA-020 | `codepotg-openapi` | closed IR/source port stable |
| TypeScript target adapter | TS-001..TS-010 | `codepotg-language-typescript` | target validation/path port and PLAN-007 stable |
| Dart target adapter | DART-001..DART-010 | `codepotg-language-dart` | target validation/path port and PLAN-007 stable |
| Jinja engine | JINJA tasks | `codepotg-template-jinja` | engine port/immutable context stable |
| Official packs | PACK-TS/PACK-DART/PACK-FLUTTER | pack packages | simplified manifest, closed kernel, PATH/PLAN, target adapters, and engine stable |
| Connected system fixture | PACK-SYSTEM, TEST-003..TEST-005 | cross-package integration | official adapters/packs and impact plan stable |

## Claim procedure

1. Select an unclaimed task whose dependencies are complete.
2. Add a row under Active claims with status `claimed`.
3. List expected files narrowly. Do not claim an entire package for a small task.
4. Change status to `in_progress` in the first implementation commit.
5. Move to `review` after implementation and tests.
6. Mark `complete` only after acceptance criteria pass and progress files are updated.
7. Remove completed claims only after the completion record exists in `PROGRESS.md`.

## Active claim row format

| Task ID | Package/subsystem | Owner/chat | Status | Expected files | Dependencies | Notes |
|---|---|---|---|---|---|---|
| CORE-001 | package foundation | chat identifier | claimed | package metadata/import tests only | DOC-001..DOC-007 | Example only; remove when making a real claim. |

## Conflict rule

Two agents must not edit the same implementation file concurrently. Closed-kernel, selector, path/name, dependency, IR, validation, plugin, and render-context contracts require narrow ownership because every adapter and pack depends on them.

## Design gates

- Core alone owns semantic objects, relations, schema kinds/roles, known facets, root-first selectors, expression roots, template contexts, and semantic validation.
- Source adapters normalize only into the known kernel and cannot register semantic extensions.
- Packs use filesystem discovery, registered `{selectionKey}` folders, fixed root-first selectors, `(expression)`, explicit imports/exports/symbols, and pack-relative `paths` arrays.
- Templates, macros, partials, and static files own every emitted character.
- Target adapters validate targets/names and calculate module/path facts; they do not render types, literals, comments, imports, exports, validators, decorators, formatting, or framework code.
- No implementation may restore neutral resource/model/entity/frontend/UI roots, reversed selectors, arbitrary query/traversal DSLs, profiles, or `filePatterns`.
- Git provider work implements direct `source.local`/`source.git` and must not introduce registries, `use`, or GitHub-only locators.
- Command work preserves exact opaque arguments and does not infer installation syntax from dependency metadata.
- Output hashes/state belong to ownership/generation state, not the dependency lock.
- Incremental generation begins only after deterministic full generation and impact analysis are proven.

## Blockers

A blocked task records the exact dependency task ID and missing contract/artifact. Generic notes such as “waiting for core” are insufficient.
