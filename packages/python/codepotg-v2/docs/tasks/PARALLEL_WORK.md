# Parallel work registry

This file coordinates work across conversations. Claim a task before changing implementation files.

## Active claims

No active implementation claims. The approved project, pack, selection-folder, direct Git source, and lock documentation is complete.

## Planned task lanes

| Lane | Task range | Primary ownership | May start when |
|---|---|---|---|
| Core primitives | CORE-001..CORE-006 | `codepotg-v2` | documentation accepted |
| Semantic naming/expressions | PATH-001..PATH-003 | core naming/path contracts | core version and diagnostics available |
| Configuration | CFG-001..CFG-006, PACKCFG-001..PACKCFG-004 | `codepotg-v2/config` | core diagnostics available |
| Fixed selectors/selection folders | PATH-004, PATH-006 | generation/config/IR contracts | typed config and selector contracts stable |
| IR/source contracts | IR-001..IR-004 | `domain/ir`, source port | core primitives and PATH-001 stable |
| Filesystem discovery/path planning | PLAN-001..PLAN-010, PATH-005, PATH-007..PATH-010 | generation domain/application | pack config, expressions, selectors, and IR stable |
| Generated imports/exports | BIND-002 plus planner tasks | generation graph + language ports | selection emissions, paths, and symbols stable |
| Plugin runtime | PLUG-001..PLUG-011 | plugins/ports/runtime | public primitives stable |
| Writers/cache | WRITE-001..WRITE-006, CACHE-001..CACHE-002 | infrastructure + ports | artifact/path plan stable |
| Commands/setup | CFG-004..CFG-005, CMD, SETUP/CONFIGURE/ECO | application/infrastructure | config/security contracts stable |
| Python API/CLI | API/CLI/MCP | api/application/cli | core use cases stable |
| Local/Git distribution | GIT/LOCK/DIST | pack provider/lock/cache | direct source and pack manifest contracts stable |
| OpenAPI adapter | OA-001..OA-012 | `codepotg-openapi` | IR/source port stable |
| TypeScript adapter | TS-001..TS-011 and TS-PATH | `codepotg-language-typescript` | language port and planned import/export contract stable |
| Dart adapter | DART-001..DART-011 and DART-PATH | `codepotg-language-dart` | language port and planned import/export contract stable |
| Jinja engine | JINJA-001..JINJA-011 | `codepotg-template-jinja` | engine port/context stable |
| Official packs | PACK-TS/PACK-DART/PACK-FLUTTER | pack packages | simplified manifest, PATH-001..PATH-010, planner, and adapters stable |

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
| PATH-001 | semantic naming | chat identifier | claimed | focused naming modules/tests only | CORE-003, IR-001 | Example only; remove when making a real claim. |

## Conflict rule

Two agents must not edit the same implementation file concurrently. Public selector, path, name, import/export, rule, IR, and plugin contracts require narrow ownership because adapters and packs depend on them.

## Design gates

- Official packs must use filesystem discovery, registered `{selectionKey}` folders, fixed selectors, `(expression)`, explicit imports/exports/symbols, and pack-relative `paths` arrays.
- Adapters must consume already planned paths and dependency descriptors; they must not parse pack source syntax or choose output directories.
- Git provider work must implement direct `source.local`/`source.git` and must not introduce `registries`, `use`, or GitHub-only locators.
- Command work must preserve exact opaque arguments and must not infer installation syntax from dependency metadata.

## Blockers

A blocked task records the exact dependency task ID and missing contract/artifact. Generic notes such as “waiting for core” are insufficient.
