# Parallel work registry

This file coordinates work across conversations. Claim a task before changing implementation files.

## Active claims

No active implementation claims. Documentation corrections through the tokenized path model are complete.

## Planned task lanes

| Lane | Task range | Primary ownership | May start when |
|---|---|---|---|
| Core primitives | CORE-001..CORE-006 | `codepotg-v2` | documentation accepted |
| Semantic naming/path values | PATH-001..PATH-002 | core naming/IR contracts | core version and diagnostics available |
| Configuration | CFG-001..CFG-016, PACKCFG-001..PACKCFG-004 | `codepotg-v2/config` | core diagnostics available |
| Path parser/recipes | PATH-003..PATH-004 | generation/config contracts | typed config and selection contracts stable |
| IR/source contracts | IR-001..IR-004 | `domain/ir`, source port | core primitives and PATH-001 stable |
| Pack discovery/path planning | PLAN-001..PLAN-010, PATH-005..PATH-010 | generation domain/application | pack config, path registry, and IR stable |
| Plugin runtime | PLUG-001..PLUG-011 | plugins/ports/runtime | public primitives stable |
| Writers/cache | WRITE-001..WRITE-006, CACHE-001..CACHE-002 | infrastructure + ports | artifact/path plan stable |
| Commands/setup | CMD-001..CMD-005, SETUP/CONFIGURE/ECO | application/infrastructure | config/security contracts stable |
| Python API/CLI | API/CLI/MCP | api/application/cli | core use cases stable |
| Git distribution | GIT/LOCK/DIST | pack provider/lock/cache | pack manifest stable |
| OpenAPI adapter | OA-001..OA-012 | `codepotg-openapi` | IR/source port stable |
| TypeScript adapter | TS-001..TS-011 | `codepotg-language-typescript` | language port/rule/path validation contract stable |
| Dart adapter | DART-001..DART-011 | `codepotg-language-dart` | language port/rule/path validation contract stable |
| Jinja engine | JINJA-001..JINJA-011 | `codepotg-template-jinja` | engine port/context stable |
| Official packs | PACK-TS/PACK-DART/PACK-FLUTTER | pack packages | manifest, PATH-001..PATH-010, planner, and adapters stable |

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

Two agents must not edit the same implementation file concurrently. Public path, name, rule, IR, and plugin contracts require narrow ownership because adapters and packs depend on them.

## Path-design gate

An official adapter or pack agent must not implement a private filename helper while PATH tasks are incomplete. It must consume the public semantic-name and path-expression contracts.

## Blockers

A blocked task records the exact dependency task ID and missing contract/artifact. Generic notes such as “waiting for core” are insufficient.
