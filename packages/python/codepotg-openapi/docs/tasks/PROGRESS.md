# OpenAPI adapter progress

| Date | Commit | Task | Status | Tests/evidence | Notes |
|---|---|---|---|---|---|
| 2026-07-26 | `12d9b8de` | Package scaffold | complete | Documentation/files only; no runtime tests. | Created package/test/task boundaries. |
| 2026-07-26 | `01041597` | Design and task contract | complete | Documentation review only; no runtime tests. | Added parse-once/direct-IR boundaries and detailed OA-001..OA-012 plan. Implementation has not started. |
| 2026-07-26 | `fb2f9e29` | Closed-kernel and `x-codegen` alignment | complete | Documentation review only. | Superseded the narrower task plan with OA-001..OA-020 and the closed-kernel mapping direction. |
| 2026-07-27 | `5430d03c` / PR #29 | OpenAPI foundation | partial | Implementing agent recorded 107 passing subsystem tests with one realistic-fixture skip in a reduced checkout. | Added options, controlled loading, parsing, reference resolution, stable IDs, and substantial schema/group/operation normalization. The PR explicitly described security, complete typed `x-codegen`, final facade, benchmarks, and release work as follow-up. |
| 2026-07-27 | PR #29 independent audit | Architecture and readiness audit | fix_required | Static merged-code audit; see `docs/audits/2026-07-27-pr-29-audit.md`. | Critical: advertised factory imports missing `codepotg_openapi.adapter`; package cannot act as a source adapter. Also found cross-session loader-cache risk, unbounded YAML alias recursion/expansion, absent public-facade/conformance/distribution tests, and README claims for missing `x-codegen`, support, and benchmark work. Added `docs/tasks/AUDIT_FIXES.md`. |

## Current implementation status

- OA-002 is an implemented foundation.
- OA-003 and OA-004 are partial and require session-isolation/parser-hardening fixes.
- OA-005 is a substantial resolver foundation.
- OA-006..OA-008 are substantial standard-normalization foundations.
- OA-016 is partial.
- OA-001, OA-017, and OA-018 remain critical blockers.
- OA-009..OA-015, OA-019, and OA-020 are not implemented.

## Immediate blockers

1. Add `src/codepotg_openapi/adapter.py` and a complete public `normalize()` pipeline.
2. Pass entry-point, import-smoke, source-adapter conformance, integration, architecture, and isolated-wheel tests.
3. Make all reference/document caches normalization-session-owned.
4. Bound YAML alias recursion, conversion depth, node/item count, and expansion.
5. Correct README/support claims to match actual implementation.
6. Implement and test typed `x-codegen` before claiming it.

The package must remain `in_progress`/`fix_required`; it is not installable as a functioning OpenAPI source adapter yet.
