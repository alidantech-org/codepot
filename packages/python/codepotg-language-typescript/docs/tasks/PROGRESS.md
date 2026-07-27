# TypeScript adapter progress

| Date | Commit | Task | Status | Tests/evidence | Notes |
|---|---|---|---|---|---|
| 2026-07-26 | `12d9b8de` | Package scaffold | complete | Documentation/files only; no runtime tests. | Created package/test/task boundaries. |
| 2026-07-26 | `01041597` | Design and task contract | complete | Documentation review only; no runtime tests. | Added typed rule/service boundaries and detailed TS-001..TS-011 plan. Implementation has not started. |
| 2026-07-26 | `8fe8dbdf` | Target path boundary | complete | Documentation review only; no runtime tests. | Locked TypeScript to target suffix/final filename validation and import use of planned paths; core owns token parsing and destination composition. |
| 2026-07-26 | `38c36169` | Non-rendering target adapter contract | complete | Reviewed package README, design, and TS-001..TS-010 task ledger; no runtime tests. | Supersedes syntax-renderer plans. The adapter now owns only suffix detection, filename/candidate validation, and module/path facts; templates author every TypeScript character. |
| 2026-07-27 | `4de8d914` | TS-001..TS-010 implementation and package review | review | Unit 58 passed; contracts 1 passed; architecture 5 passed; integration 1 passed; TypeScript compiler oracle 1 passed; performance 1 passed; distribution/combined entry points 4 passed; complete suite 71 passed. Local setuptools PEP 517 backend produced wheel and sdist; isolated and combined non-editable wheel calls passed against the reconstructed public-contract core harness. | Exact repository-core suite, Ruff commands, `python -m build`, and real core-wheel installation remain unverified because the execution environment cannot obtain a checkout or the missing tools. The feature branch must not merge until those required checks pass. |

## Exact blocked public contracts

- Validation requests do not carry source provenance or `SourceSpan` fields.
- The target adapter protocol does not expose cancellation.
- `ModulePathFacts` has no diagnostics field, so unsupported requests use stable `TS_MODULE_PATH_INVALID:` and `TS_MODULE_PATH_UNSUPPORTED:` `ValueError` prefixes.
- Module requests do not expose symbols, semantic type-only versus value-use facts, provider export/barrel role, target compatibility metadata, planner-owned alias descriptors, module-resolution mode, TypeScript runtime extension mode, or multiple candidate provider artifacts.
- Core has no typed project/pack configuration bridge for decoding adapter options.
- TS-009 official rendered integration remains blocked on an installable official Jinja engine, pack contracts, and the missing core planning facts. The package-local integration fixture proves only public adapter facts and authored syntax ownership.
