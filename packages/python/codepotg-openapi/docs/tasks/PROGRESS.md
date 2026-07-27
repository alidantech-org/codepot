# OpenAPI adapter progress

| Date | Commit | Task | Status | Tests/evidence | Notes |
|---|---|---|---|---|---|
| 2026-07-26 | `12d9b8de` | Package scaffold | complete | Documentation/files only; no runtime tests. | Created package/test/task boundaries. |
| 2026-07-26 | `01041597` | Design and task contract | complete | Documentation review only; no runtime tests. | Added parse-once/direct-IR boundaries and detailed OA-001..OA-012 plan. Implementation had not started. |
| 2026-07-26 | `fb2f9e29` | Closed-kernel and `x-codegen` alignment | complete | Documentation review only. | Superseded the narrower task plan with OA-001..OA-020 and the closed-kernel mapping direction. |
| 2026-07-27 | `5430d03c` / PR #29 | OpenAPI foundation | partial | Implementing agent recorded 107 passing subsystem tests with one realistic-fixture skip in a reduced checkout. | Added options, controlled loading, parsing, reference resolution, stable IDs, and substantial schema/group/operation normalization. The PR explicitly described security, complete typed `x-codegen`, final facade, benchmarks, and release work as follow-up. |
| 2026-07-27 | PR #29 independent audit | Architecture and readiness audit | fix_required | Static merged-code audit; see `docs/audits/2026-07-27-pr-29-audit.md`. | Found the missing adapter/factory path, cross-session loader cache, unbounded YAML alias conversion, absent facade/conformance/distribution tests, and unsupported README claims. |
| 2026-07-27 | `f7aacba0`, `e1a7a11b` | OA-001/OA-017 public adapter and composed standard pipeline | review | Added public protocol, factory/import, conformance, success/failure, cancellation, core-validation, and deterministic-result tests. | `OpenApiSourceAdapter.normalize()` now composes one standard OpenAPI session and returns only public core types. |
| 2026-07-27 | `01efbe19`, `ea266a51` | OA-003/OA-005 session isolation | review | Added same-adapter changed-content and controlled-reference two-session tests; local loading-session harness **3/3 passed**. | `ControlledSourceLoader` is stateless authority; `SourceLoadingSession` owns one-call reference bytes. |
| 2026-07-27 | `6b5296b0`, `5d454d43` | OA-004 YAML hardening | review | Added recursive-alias, alias-expansion, depth, node-count, and option tests; local adversarial parser harness **5/5 passed**. | Added behavior-versioned `maxYamlDepth`, `maxYamlNodes`, and `maxYamlAliases` limits with stable diagnostics. |
| 2026-07-27 | `482c1649`, `456304e1`, `1d8c8980` | Capability/provenance audit repairs | review | Architecture tests prohibit private core, target, template, writer, and missing `x_codegen` ownership. | Removed false typed-`x-codegen` capability/import and corrected external Path Item source provenance. |
| 2026-07-27 | `7730e4de`, `4dc07395`, `c0979437` | OA-018 public, security, architecture, and distribution test suites | review | Tests added for entry point, import, shared conformance, real standard contract, deterministic JSON/YAML digest, cancellation, authority denial, session isolation, YAML attacks, wheel contents, and isolated wheel invocation. | Tests target the actual sibling `codepotg-v2` public package; no compatibility runtime was added. |
| 2026-07-27 | `33fcfeba`, `b0144cad`, `ec872164` | Truthful support and audit resolution | review | README/support/audit-resolution review. | Standard OpenAPI support is documented. OA-009 security and OA-010..OA-015 typed semantics remain explicitly unimplemented; security and `x-codegen` inputs emit diagnostics. |
| 2026-07-27 | PR #36 | Synchronize concurrent base work | complete | Branch comparison after merge: repair branch **22 commits ahead, 0 behind** the then-current base. | Preserved concurrent author, language-adapter, Jinja, and coordination changes without force-pushing. |

## Current implementation status

- OA-001 and OA-017 are implemented and in review pending the complete synchronized release command set.
- OA-002 is integrated into result behavior/digest identity; YAML safety options were added.
- OA-003 and OA-005 now use one loading/reference cache session per `normalize()` call.
- OA-004 includes recursive-alias, depth, expanded-node, alias-count, and recursion boundaries.
- OA-006..OA-008 provide the current standard structural schema/group/operation subset and final core validation.
- OA-016 remains partial for complete bounded preservation coverage.
- OA-018 test coverage is implemented but remains review until all committed tests run in a synchronized checkout.
- OA-009..OA-015 and OA-019 remain not implemented.
- OA-020 documentation is partially implemented; release verification remains open.

## Verification completed in this environment

- Changed Python source/test syntax and compile checks passed on the repair drafts.
- Adversarial YAML parser harness: **5/5 passed**.
- Loading-session isolation harness: **3/3 passed**.
- GitHub branch scope comparison confirms changes are limited to `packages/python/codepotg-openapi/**`; `.github/**` is untouched.

## Release verification still required

This environment cannot resolve GitHub or package-index DNS and cannot obtain a full executable repository checkout. Therefore it does **not** claim the complete package suite, Ruff, build, or real-wheel installation passed here.

Run from `packages/python/codepotg-openapi` in a synchronized checkout:

```bash
python -m pip install -e ../codepotg-v2 -e '.[dev]'
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest -q
python -m build
```

Then install freshly built `codepotg-core` and `codepotg-openapi` wheels into an isolated environment and invoke the `codepotg.source_adapters/openapi` entry point. Only after those results are appended here should OA-001/OA-017/OA-018 move from `review` to `complete`.
