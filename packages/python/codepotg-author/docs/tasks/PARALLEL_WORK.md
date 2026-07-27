# codepotg-author parallel work registry

Claim a narrow task range before changing implementation files. The package has one public API/ref/compiler owner at a time.

## Active claims

| Task ID | Subsystem | Owner/chat | Status | Expected files | Dependencies | Notes |
|---|---|---|---|---|---|---|

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
