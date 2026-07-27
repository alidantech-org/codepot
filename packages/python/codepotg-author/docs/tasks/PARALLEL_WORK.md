# codepotg-author parallel work registry

Claim a narrow task range before changing implementation files. The package has one public API/ref/compiler owner at a time.

## Active claims

| Task ID | Subsystem | Owner/chat | Status | Expected files | Dependencies | Notes |
|---|---|---|---|---|---|---|
| AUTHOR-001..AUTHOR-013, AUTHOR-015..AUTHOR-020, AUTHOR-022, AUTHOR-024, AUTHOR-027..AUTHOR-030 | Typed Python authoring compiler, current-core semantic builders, canonical transport, verification, and documentation | GPT-5.6 Thinking / CODEPOT session 2026-07-27 | claimed | `pyproject.toml`; `README.md`; `src/codepotg_author/**`; mirrored `tests/**`; `examples/**`; `benchmarks/**`; `docs/tasks/{PARALLEL_WORK,PROGRESS}.md`; public API/support documentation | Public `codepotg.ir`, `codepotg.diagnostics`, naming, versions, and validation facades at base `82796179` | AUTHOR-014, AUTHOR-021, AUTHOR-023, AUTHOR-025, AUTHOR-026, extended AUTHOR-019, and public-codec ownership in AUTHOR-028 remain blocked on exact public core contracts. Unsupported declarations will return `AUTHOR_CORE_UNSUPPORTED` and will not enter IR/extensions/raw. |

## Available lanes

| Lane | Tasks | May start when |
|---|---|---|
| Foundation/ref API | AUTHOR-001..AUTHOR-008 | immediately after scaffold audit |
| Properties/schemas | AUTHOR-009..AUTHOR-013 | public ref and diagnostic contracts committed |
| Current-core semantic builders | AUTHOR-015..AUTHOR-020, AUTHOR-022, AUTHOR-024 | schema refs and public core mapping stable |
| Compiler | AUTHOR-027 | declaration models and current-core builders stable |
| Transport | AUTHOR-028 | canonical core mapping and codec ownership decision stable |
| Tests/release | AUTHOR-029..AUTHOR-030 | subsystem APIs committed |
| Kernel evolution | AUTHOR-014, AUTHOR-021, AUTHOR-023, AUTHOR-025, AUTHOR-026 and extended AUTHOR-019/028 | separate approved core ownership |

## Claim procedure

1. Add a row with status `claimed`.
2. List exact files and dependencies.
3. Move to `in_progress` in the first implementation commit.
4. Append evidence to `PROGRESS.md` after every coherent batch.
5. Move to `review` only after focused and complete package checks pass.
6. Mark `complete` only after every release gate passes.

## Conflict rule

No two agents edit the same public API, ref, declaration, compiler context, pass, transport schema, or task row concurrently. Preserve every other package lane when synchronizing core coordination files.
