# OpenAPI adapter progress

| Date | Commit | Task | Status | Tests/evidence | Notes |
|---|---|---|---|---|---|
| 2026-07-26 | `12d9b8de` | Package scaffold | complete | Documentation/files only; no runtime tests. | Created package/test/task boundaries. |
| 2026-07-26 | `01041597` | Design and task contract | complete | Documentation review only; no runtime tests. | Added parse-once/direct-IR boundaries and detailed OA-001..OA-012 plan. Implementation has not started. |
| 2026-07-26 | `fb2f9e29` | Closed-kernel and `x-codegen` alignment | complete | Reviewed package README, design, and OA-001..OA-020 task ledger; no runtime tests because implementation has not started. | Supersedes the narrower OA-001..OA-012 plan. OpenAPI now maps into groups, structural schemas, operation I/O/failures/effects, known facets, storage mappings, views, policies/access, events/listeners, execution hooks, workflows, and compensation without extending the kernel. |
