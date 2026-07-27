# Jinja engine progress

| Date | Commit | Task | Status | Tests/evidence | Notes |
|---|---|---|---|---|---|
| 2026-07-26 | `12d9b8de` | Package scaffold | complete | Documentation/files only; no runtime tests. | Created package/test/task boundaries. |
| 2026-07-26 | `01041597` | Design and task contract | complete | Documentation review only; no runtime tests. | Added sandbox/context/include/cache boundaries and detailed JINJA-001..JINJA-011 plan. Implementation had not started. |
| 2026-07-27 | `26b4ca46` | JINJA claim | complete | Starting base `686d8a9c`; coordination diff limited to `PARALLEL_WORK.md`. | The requested nested branch could not exist below the existing `chatgpt/codepotx-restart` ref; the approved compatible branch was `chatgpt/codepotx-restart-codepotg-template-jinja`. JINJA-008 remained unclaimed. |
| 2026-07-27 | `fbe6627f` | JINJA-001, JINJA-002 foundation | complete | Package metadata, typing marker, entry-point declaration, immutable rule validation, metadata/rule tests. | Strict defaults are host-controlled and never read from context or host state. |
| 2026-07-27 | `aeb1be8e` | JINJA-003, JINJA-009 context/helpers/cache | complete | Safe public semantic snapshots, documented `Name` projections, helper conflict/version tests, bounded concurrent cache tests. | Caller `Name` cached projections are read from a clone so source objects remain unchanged. |
| 2026-07-27 | `83b566e4` | JINJA-004..JINJA-006 sandbox and declared dependencies | complete | Registry-ID, partial-limit, AST, static include/import/inheritance, cycle/depth, no-default-global, and loader tests. | Uses only an immutable in-memory loader; no filesystem or pack-provider fallback exists. |
| 2026-07-27 | `29063da5` | JINJA-007 bounded engine | complete | Public port conformance, real IR rendering, strict undefined, streamed byte limit, cancellation, diagnostics, and cache invalidation/concurrency tests. | Cancellation returns `JINJA_CANCELLED` with no partial content. |
| 2026-07-27 | `0d9ef90e` | JINJA-010 architecture/security/integration | complete | Adversarial dunder/global/callable/dependency probes; filesystem, environment, process, and network denial guards; import-side-effect and ownership tests. | No `.github` file or automation was created. |
| 2026-07-27 | `21401e56` | JINJA-011 distribution and benchmark tooling | implemented | Isolated v1/v2 JSON runners, 13 neutral cases, one warm-up, seven cold/warm measurements, wheel-content and isolated entry-point/static-partial tests. | Machine-specific benchmark output remains ignored and uncommitted. |
| 2026-07-27 | local verification | Initial package verification | review | Complete suite 150 passed; `compileall` passed; wheel and sdist built; isolated discovery/render tests passed. | Used a snapshot of public core contracts. Ruff and complete synchronized real-core verification remained open. |
| 2026-07-27 | local benchmark | v2 benchmark evidence | complete | 13 cases, one warm-up, seven measured cold/warm iterations; exact SHA-256 and byte counts recorded; strict undefined=`JINJA_UNDEFINED`; syntax failure=`JINJA_SYNTAX`; warm cache hits observed. | Machine timings are intentionally not committed. |
| 2026-07-27 | PR #28 independent audit | Architecture and readiness audit | review | Static merged-code audit; see `docs/audits/2026-07-27-pr-28-audit.md`. | Implementation was safe to keep merged, but release verification remained open. |
| 2026-07-27 | `b8b24fd4`, `09970fd3` | JINJA-AUDIT-004 and JINJA-AUDIT-005 code fixes | implemented | Added exact `loop.cycle()`/`loop.changed()` denial coverage and malformed-root-source diagnostic coverage. Root sources use `JINJA_TEMPLATE_INVALID`; partial sources remain `JINJA_PARTIAL_INVALID`. | Named outputs and missing pack/planner/config/cache-port contracts remain blocked and were not emulated. |
| 2026-07-27 | targeted audit smoke | Audit behavior validation | passed | Both loop calls were denied; root/partial source selector smoke produced `JINJA_TEMPLATE_INVALID` and `JINJA_PARTIAL_INVALID`. | Focused behavior smoke only. |
| 2026-07-27 | release environment probe | Initial tool availability | superseded | Direct clone and package-index access failed because external DNS/package mirrors were unavailable. | Replaced by authenticated GitHub source reconstruction plus official Ruff and PyPA Build artifacts. |
| 2026-07-27 | `chatgpt/codepotx-restart-jinja-release-gates` | JINJA-011 and PR #28 release gates | complete | Core: 30 tests passed; Ruff check passed; 59 files formatted; wheel/sdist built. Jinja: 153 tests passed; Ruff check passed; 65 files formatted; wheel/sdist built. Fresh wheel-only environment discovered the `jinja` entry point, rendered `Hello World`, rendered static partials as `ABC`, and returned `JINJA_CALLABLE_DENIED` for `loop.cycle()`. | Exact current-branch package files were retrieved through the authenticated GitHub contents API and checked against GitHub blob identities. Official Ruff 0.16.0 and PyPA Build 1.5.0 artifacts were used. No core implementation or `.github/**` file changed. |

## Exact release commands

From `packages/python/codepotg-v2`:

```bash
python -m pytest -q
ruff check src tests
ruff format --check src tests
python -m build --no-isolation
```

Results:

```text
30 passed in 4.09s
All checks passed!
59 files already formatted
Successfully built codepotg_core-2.0.0a1.tar.gz and codepotg_core-2.0.0a1-py3-none-any.whl
```

From `packages/python/codepotg-template-jinja`:

```bash
python -m pytest -q
ruff check src tests benchmarks
ruff format --check src tests benchmarks
python -m build --no-isolation
```

Results:

```text
153 passed in 10.85s
All checks passed!
65 files already formatted
Successfully built codepotg_template_jinja-2.0.0a1.tar.gz and codepotg_template_jinja-2.0.0a1-py3-none-any.whl
```

`--no-isolation` was required because the external package mirror was unavailable. The declared setuptools backend and its build requirements were installed in the verification environment before the commands ran.

## Built artifact evidence

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `codepotg_core-2.0.0a1-py3-none-any.whl` | 35,698 | `004c29c1a090554fc6d88a960bb537b4003af0004285719bb270ad2e9e41fd84` |
| `codepotg_core-2.0.0a1.tar.gz` | 23,500 | `8efdb996af33daac533e8e6860ba4b9c802f719991ac8be117e2f3ec0fe8505f` |
| `codepotg_template_jinja-2.0.0a1-py3-none-any.whl` | 25,614 | `1de62952e584c56ceca2e827e99a73a561720ecb642abdc0a2c4a960c0c25350` |
| `codepotg_template_jinja-2.0.0a1.tar.gz` | 17,825 | `15a0f93c0789752bbab300ffa940a798c7890795dc929c6fcf8e8eec9df03971` |

## Current status

JINJA-001..JINJA-007, JINJA-009, JINJA-010, and JINJA-011 are complete for the current public `TemplateEngine` port.

The following remain intentionally blocked until public contracts exist:

- JINJA-008 named outputs;
- pack-registry integration;
- target-compatible partial metadata;
- project/pack rule decoding;
- runtime cache-port integration.

The isolated v1 benchmark remains optional comparative performance work. It is not a current-port correctness or release gate and does not change the completed JINJA-011 status.
