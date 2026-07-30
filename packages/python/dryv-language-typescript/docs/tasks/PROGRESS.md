# TypeScript adapter progress

| Date | Commit | Task | Status | Tests/evidence | Notes |
|---|---|---|---|---|---|
| 2026-07-26 | `12d9b8de` | Package scaffold | complete | Documentation/files only; no runtime tests. | Created package/test/task boundaries. |
| 2026-07-26 | `01041597` | Design and task contract | complete | Documentation review only; no runtime tests. | Added typed rule/service boundaries and detailed TypeScript task plan. |
| 2026-07-26 | `8fe8dbdf` | Target path boundary | complete | Documentation review only. | Locked TypeScript to target suffix/final filename validation and planned-path facts. |
| 2026-07-26 | `38c36169` | Non-rendering target adapter contract | complete | Documentation review only. | Superseded syntax-renderer plans. Templates own every TypeScript character. |
| 2026-07-27 | `4de8d914` / PR #30 | TS-001..TS-010 implementation | review | Unit 58 passed; contracts 1; architecture 5; integration 1; TypeScript compiler oracle 1; performance 1; distribution/combined entry points 4; complete suite 71 passed. Local harness produced wheel/sdist and isolated calls. | Exact synchronized core suite, Ruff, `python -m build`, and real core-wheel installation remained unverified when the PR was merged. |
| 2026-07-27 | PR #30 independent audit | Architecture and readiness audit | review_fix_required | Static merged-code audit; see `docs/audits/2026-07-27-pr-30-audit.md`. | Architecture is correct. Required source fix: direct `TypeScriptTargetOptions(...)` accepted raw strings/non-enum values that later failed identity comparisons and silently altered behavior. Distribution checks could skip before build. Added `docs/tasks/AUDIT_FIXES.md` and reconciled task statuses. |
| 2026-07-27 | `5f0bf45e..1432960f` | TS-AUDIT-001, TS-AUDIT-003, TS-AUDIT-005 repair | review | Targeted runtime validation smoke checks passed for raw policy strings, invalid package values, malformed aliases, and valid enum values. Added non-skipping fresh wheel/sdist build inspection and exact distribution/plugin version assertions. | Source defects were repaired on `chatgpt/codepotx-restart-typescript-audit-fixes`; synchronized release verification was still open at this checkpoint. |
| 2026-07-27 | `94f13e97`, `09a8fd35`, `974aaffc` | Synchronized release verification and dual-wheel hardening | complete_current_port | User-supplied full logs confirm synchronized core and adapter Ruff/format checks, complete test suites, exact builds, TypeScript 5.9 compiler oracle, real-wheel installation and smoke calls, and a clean tracked tree. The combined distribution test now builds the core, TypeScript, and Dart wheels, installs them in a fresh virtual environment with `--no-index`, and requires both entry points without any skip path. | TS-010 is release-verified for the current public `TargetAdapter` port. TS-006 and TS-009 remain intentionally partial until core exposes the required planner/module facts and an official pack pipeline. |

## Exact blocked public contracts

- Validation requests do not carry source provenance or `SourceSpan` fields.
- The target adapter protocol does not expose cancellation.
- `ModulePathFacts` has no diagnostics field, so unsupported requests use stable `TS_MODULE_PATH_INVALID:` and `TS_MODULE_PATH_UNSUPPORTED:` `ValueError` prefixes.
- Module requests do not expose symbols, semantic type-only/value-use facts, provider export/barrel role, target compatibility metadata, planner-owned alias descriptors, module-resolution mode, runtime extension mode, or multiple provider artifacts.
- Core has no typed project/pack configuration bridge for adapter options.
- TS-009 official rendering remains blocked on planner/pack facts and an official pack pipeline.

## Remaining work

- Implement TS-006 only after the public planner/module contract exposes the missing dependency facts and a diagnostic channel.
- Implement TS-009 only through the official planner, Jinja engine, and TypeScript pack pipeline.
- Keep the isolated three-wheel entry-point test mandatory in future release verification; it must fail rather than skip when either adapter is missing or unloadable.
