# Dart adapter progress

| Date | Commit | Task | Status | Tests/evidence | Notes |
|---|---|---|---|---|---|
| 2026-07-26 | `12d9b8de` | Package scaffold | complete | Documentation/files only; no runtime tests. | Created package/test/task boundaries. |
| 2026-07-26 | `01041597` | Design and task contract | complete | Documentation review only; no runtime tests. | Added typed rule/service boundaries and detailed DART-001..DART-011 plan. Implementation has not started. |
| 2026-07-26 | `8fe8dbdf` | Target path boundary | complete | Documentation review only; no runtime tests. | Locked Dart to target suffix/final filename validation and import use of planned paths; core owns token parsing and destination composition. |
| 2026-07-26 | `8c2d173d` | Non-rendering target adapter contract | complete | Reviewed package README, design, and DART-001..DART-010 task ledger; no runtime tests. | Supersedes type/import/export renderer plans. The adapter now owns only Dart suffix, filename/candidate validation, and URI/path facts; templates author every Dart character. |
| 2026-07-27 | `4de8d914` | DART-001..DART-010 implementation and package review | review | Unit 72 passed; contracts 1 passed; architecture 5 passed; integration 1 passed; Dart SDK oracle 1 honest skip; performance 1 passed; distribution 3 passed; complete suite 83 passed and 1 skipped. Local setuptools PEP 517 backend produced wheel and sdist; isolated and combined non-editable wheel calls passed against the reconstructed public-contract core harness. | Exact repository-core suite, Ruff commands, `python -m build`, real core-wheel installation, and the Dart compiler oracle remain unverified because the execution environment lacks the checkout/tooling and Dart SDK. The feature branch must not merge until required checks pass. |

## Exact blocked public contracts

- Validation requests do not carry source provenance or `SourceSpan` fields.
- The target adapter protocol does not expose cancellation.
- `ModulePathFacts` has no diagnostics field, so unsupported requests use stable `DART_MODULE_PATH_INVALID:` and `DART_MODULE_PATH_UNSUPPORTED:` `ValueError` prefixes.
- Module requests do not expose symbols, provider export/barrel role, target compatibility metadata, planner-owned aliases, module-resolution mode, Dart library-root metadata, or multiple candidate provider artifacts.
- Core has no typed project/pack configuration bridge for decoding adapter options.
- DART-009 official rendered integration remains blocked on an installable official Jinja engine, pack contracts, and the missing core planning facts. The package-local integration fixture proves only public adapter facts and authored syntax ownership.
