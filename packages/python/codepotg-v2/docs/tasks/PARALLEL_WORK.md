# Parallel work registry

This file coordinates work across conversations. Claim a task before changing implementation files.

## Active claims

| Task ID | Package/subsystem | Owner/chat | Status | Expected files | Dependencies | Notes |
|---|---|---|---|---|---|---|
| DOC-001 | Core architecture documentation | current chat | in_progress | `docs/**`, package task docs | none | Expanding the approved design and removing compatibility-runtime tasks. |

## Planned task lanes

| Lane | Task range | Primary ownership | May start when |
|---|---|---|---|
| Core primitives | CORE-001..CORE-020 | `codepotg-v2` | documentation locked |
| Configuration | CFG-001..CFG-040 | `codepotg-v2/config` | core diagnostic primitives available |
| IR/source contracts | IR-001..IR-030 | `codepotg-v2/domain/ir`, source port | core primitives available |
| Pack/file planning | PLAN-001..PLAN-050 | generation domain/application | config models and IR contracts stable |
| Plugin runtime | PLUG-001..PLUG-030 | plugins/ports/runtime | public primitives stable |
| Writers/cache | WRITE-001..WRITE-030 | infrastructure + ports | artifact plan stable |
| Commands/setup | CMD-001..CMD-035 | application/infrastructure | config/security contracts stable |
| Python API/CLI | API-001..API-025 | api/application/cli | core use cases stable |
| Git distribution | GIT-001..GIT-020 | pack provider/lock/cache | pack manifest stable |
| OpenAPI adapter | OA-001.. | `codepotg-openapi` | IR/source port stable |
| TypeScript adapter | TS-001.. | `codepotg-language-typescript` | language port/rule protocol stable |
| Dart adapter | DART-001.. | `codepotg-language-dart` | language port/rule protocol stable |
| Jinja engine | JINJA-001.. | `codepotg-template-jinja` | engine port/context stable |
| Official packs | PACK-TS/PACK-DART/PACK-FLUTTER | pack packages | manifest/planner/adapters stable |

## Claim procedure

1. Select an unclaimed task whose dependencies are complete.
2. Add a row under Active claims with status `claimed`.
3. List expected files narrowly. Do not claim an entire package for a small task.
4. Change status to `in_progress` in the first implementation commit.
5. Move to `review` after implementation and tests.
6. Mark `complete` only after acceptance criteria pass and progress files are updated.
7. Remove completed claims from Active claims only after the completion record exists in `PROGRESS.md`.

## Conflict rule

Two agents must not edit the same implementation file concurrently. Documentation task files may only be edited by the task owner unless coordination is recorded here.

## Blockers

A blocked task records the exact dependency task ID and the missing contract or artifact. Generic notes such as “waiting for core” are insufficient.
