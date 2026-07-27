# TypeScript adapter progress

| Date | Commit | Task | Status | Tests/evidence | Notes |
|---|---|---|---|---|---|
| 2026-07-26 | `12d9b8de` | Package scaffold | complete | Documentation/files only; no runtime tests. | Created package/test/task boundaries. |
| 2026-07-26 | `01041597` | Design and task contract | complete | Documentation review only; no runtime tests. | Added typed rule/service boundaries and detailed TypeScript task plan. |
| 2026-07-26 | `8fe8dbdf` | Target path boundary | complete | Documentation review only. | Locked TypeScript to target suffix/final filename validation and planned-path facts. |
| 2026-07-26 | `38c36169` | Non-rendering target adapter contract | complete | Documentation review only. | Superseded syntax-renderer plans. Templates own every TypeScript character. |
| 2026-07-27 | `4de8d914` / PR #30 | TS-001..TS-010 implementation | review | Unit 58 passed; contracts 1; architecture 5; integration 1; TypeScript compiler oracle 1; performance 1; distribution/combined entry points 4; complete suite 71 passed. Local harness produced wheel/sdist and isolated calls. | Exact synchronized core suite, Ruff, `python -m build`, and real core-wheel installation remained unverified when the PR was merged. |
| 2026-07-27 | PR #30 independent audit | Architecture and readiness audit | review_fix_required | Static merged-code audit; see `docs/audits/2026-07-27-pr-30-audit.md`. | Architecture is correct. Required source fix: direct `TypeScriptTargetOptions(...)` accepts raw strings/non-enum values that later fail identity comparisons and silently alter behavior. Distribution checks can skip before build. Added `docs/tasks/AUDIT_FIXES.md` and reconciled task statuses. |
| 2026-07-27 | `5f0bf45e..1432960f` | TS-AUDIT-001, TS-AUDIT-003, TS-AUDIT-005 repair | review | Targeted runtime validation smoke checks passed for raw policy strings, invalid package values, malformed aliases, and valid enum values. Added non-skipping fresh wheel/sdist build inspection and exact distribution/plugin version assertions. | Source defects are repaired on `chatgpt/codepotx-restart-typescript-audit-fixes`. The current environment cannot clone GitHub or install Ruff/`build` from its package mirror, so synchronized full-suite, exact release build, and real-wheel verification remain open and are not claimed. |

## Exact blocked public contracts

- Validation requests do not carry source provenance or `SourceSpan` fields.
- The target adapter protocol does not expose cancellation.
- `ModulePathFacts` has no diagnostics field, so unsupported requests use stable `TS_MODULE_PATH_INVALID:` and `TS_MODULE_PATH_UNSUPPORTED:` `ValueError` prefixes.
- Module requests do not expose symbols, semantic type-only/value-use facts, provider export/barrel role, target compatibility metadata, planner-owned alias descriptors, module-resolution mode, runtime extension mode, or multiple provider artifacts.
- Core has no typed project/pack configuration bridge for adapter options.
- TS-009 official rendering remains blocked on planner/pack facts and an official pack pipeline.

## Open release/fix gates

- Run Ruff, format, complete core/package suites, and the exact `python -m build` release command on the synchronized checkout.
- Install the real core and TypeScript wheels in a fresh environment and repeat entry-point/module-path calls.
- Re-run the TypeScript compiler oracle against the synchronized checkout.
- Record exact evidence and a clean working tree before marking TS-010 complete.
