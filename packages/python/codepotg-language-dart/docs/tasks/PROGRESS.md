# Dart adapter progress

| Date | Commit | Task | Status | Tests/evidence | Notes |
|---|---|---|---|---|---|
| 2026-07-26 | `12d9b8de` | Package scaffold | complete | Documentation/files only; no runtime tests. | Created package/test/task boundaries. |
| 2026-07-26 | `01041597` | Design and task contract | complete | Documentation review only. | Added typed rule/service boundaries and detailed Dart task plan. |
| 2026-07-26 | `8fe8dbdf` | Target path boundary | complete | Documentation review only. | Locked Dart to target suffix/final filename validation and planned-path facts. |
| 2026-07-26 | `8c2d173d` | Non-rendering target adapter contract | complete | Documentation review only. | Superseded renderer plans. Templates own every Dart character. |
| 2026-07-27 | `4de8d914` / PR #30 | DART-001..DART-010 implementation | review | Unit 72 passed; contracts 1; architecture 5; integration 1; Dart SDK oracle 1 honest skip; performance 1; distribution 3; complete suite 83 passed and 1 skipped. Local harness produced wheel/sdist and isolated calls. | Exact synchronized core suite, Ruff, `python -m build`, real core-wheel installation, and a real Dart SDK oracle remained unverified when merged. |
| 2026-07-27 | PR #30 independent audit | Architecture and readiness audit | review_fix_required | Static merged-code audit; see `docs/audits/2026-07-27-pr-30-audit.md`. | Architecture is correct. Required source fix: direct `DartTargetOptions(...)` accepts raw strings/non-enum values that later fail identity comparisons and silently alter behavior. Distribution checks can skip before build. Added `docs/tasks/AUDIT_FIXES.md` and reconciled task statuses. |
| 2026-07-27 | `1113f596..e55890f5` | DART-AUDIT-001, DART-AUDIT-004, DART-AUDIT-006 repair | review | Targeted runtime validation smoke checks passed for raw policy strings, invalid package/boolean values, and valid enum values. Added non-skipping fresh wheel/sdist build inspection and exact distribution/plugin version assertions. | Source defects are repaired on `chatgpt/codepotx-restart-dart-audit-fixes`. The current environment cannot clone GitHub or install Ruff/`build` from its package mirror, and no Dart SDK is available, so synchronized full-suite, exact release build, real-wheel verification, and the SDK oracle remain open and are not claimed. |

## Exact blocked public contracts

- Validation requests do not carry source provenance or `SourceSpan` fields.
- The target adapter protocol does not expose cancellation.
- `ModulePathFacts` has no diagnostics field, so unsupported requests use stable `DART_MODULE_PATH_INVALID:` and `DART_MODULE_PATH_UNSUPPORTED:` `ValueError` prefixes.
- Module requests do not expose symbols, provider export/barrel role, target compatibility metadata, planner-owned aliases, module-resolution mode, Dart library-root metadata, or multiple provider artifacts.
- Core has no typed project/pack configuration bridge for adapter options.
- DART-009 official rendering remains blocked on planner/pack facts and an official pack pipeline.

## Open release/fix gates

- Run Ruff, format, complete core/package suites, and the exact `python -m build` release command on the synchronized checkout.
- Install the real core and Dart wheels in a fresh environment and repeat entry-point/URI calls.
- Run representative fixtures through a real Dart SDK.
- Record exact evidence and a clean working tree before marking DART-010 complete.
