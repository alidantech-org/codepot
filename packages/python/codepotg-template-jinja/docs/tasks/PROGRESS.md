# Jinja engine progress

| Date | Commit | Task | Status | Tests/evidence | Notes |
|---|---|---|---|---|---|
| 2026-07-26 | `12d9b8de` | Package scaffold | complete | Documentation/files only; no runtime tests. | Created package/test/task boundaries. |
| 2026-07-26 | `01041597` | Design and task contract | complete | Documentation review only; no runtime tests. | Added sandbox/context/include/cache boundaries and detailed JINJA-001..JINJA-011 plan. Implementation has not started. |
| 2026-07-27 | `26b4ca46` | JINJA claim | complete | Starting base `686d8a9c`; coordination diff limited to `PARALLEL_WORK.md`. | The requested nested branch could not exist below the existing `chatgpt/codepotx-restart` ref; the approved compatible branch is `chatgpt/codepotx-restart-codepotg-template-jinja`. JINJA-008 remains unclaimed. |
| 2026-07-27 | `fbe6627f` | JINJA-001, JINJA-002 foundation | complete | Package metadata, typing marker, entry-point declaration, immutable rule validation, metadata/rule tests. | Claim moved to `in_progress`; strict defaults are host-controlled and never read from context or host state. |
| 2026-07-27 | `aeb1be8e` | JINJA-003, JINJA-009 context/helpers/cache | complete | Safe public semantic snapshots, documented `Name` projections, helper conflict/version tests, bounded concurrent cache tests. | Caller `Name` cached projections are read from a clone so source objects remain unchanged. |
| 2026-07-27 | `83b566e4` | JINJA-004..JINJA-006 sandbox and declared dependencies | complete | Registry-ID, partial-limit, AST, static include/import/inheritance, cycle/depth, no-default-global, and loader tests. | Uses only an immutable in-memory loader; no filesystem or pack-provider fallback exists. |
| 2026-07-27 | `29063da5` | JINJA-007 bounded engine | complete | Public port conformance, real IR rendering, strict undefined, streamed byte limit, cancellation, diagnostics, and cache invalidation/concurrency tests. | Cancellation returns `JINJA_CANCELLED` with no partial content. |
| 2026-07-27 | `0d9ef90e` | JINJA-010 architecture/security/integration | complete | Adversarial dunder/global/callable/dependency probes; filesystem, environment, process, and network denial guards; import-side-effect and ownership tests. | No `.github` file or automation was created. |
| 2026-07-27 | `21401e56` | JINJA-011 distribution and benchmark tooling | complete | Isolated v1/v2 JSON runners, 13 neutral cases, one warm-up, seven cold/warm measurements, wheel-content and isolated entry-point/static-partial tests. | Machine-specific benchmark output remains ignored and uncommitted. |
| 2026-07-27 | local verification | Package verification | in_progress | Unit 68 passed; contract 6 passed; architecture 9 passed; security 37 passed; integration 21 passed; performance 5 passed; distribution 4 passed; complete suite 150 passed in 10.66s; `compileall` passed; wheel and sdist built through the PEP 517 setuptools backend; isolated discovery/render tests passed. | Local execution used a snapshot of the exact published public core contracts because external DNS/package downloads and a full repository archive were blocked. Ruff and the complete real-core suite remain release gates; no completion or merge is claimed yet. |
| 2026-07-27 | local benchmark | v2 benchmark evidence | complete | 13 cases, one warm-up, seven measured cold/warm iterations; exact SHA-256 and byte counts recorded; strict undefined=`JINJA_UNDEFINED`; syntax failure=`JINJA_SYNTAX`; warm cache hits observed. | Machine timings are intentionally not committed. The v1 runner must execute separately in a v1 environment before any cross-version speed or memory conclusion. |
| 2026-07-27 | documentation audit | Old baseline reading | partial | Read old `pyproject.toml`, renderer, emission engine, renderer tests, memory profiler, performance guide, and `docs/packages/codepotg/jinja-templates.md`. | Requested baseline path `packages/python/codepotg/docs/jinja-templates.md` does not exist at base `686d8a9c`; no replacement content was invented or copied. |

## Open release gates

- Run `python -m ruff check src tests benchmarks` and `python -m ruff format --check src tests benchmarks` with an available Ruff installation.
- Run the complete `codepotg-v2` verification suite and build from the real synchronized repository checkout.
- Re-run the complete Jinja suite against that real core package.
- Build/install the real core and Jinja wheels together in a fresh isolated environment and repeat entry-point discovery.
- Run the isolated v1 benchmark in a CodepotG 1.0.0 environment and compare neutral output hashes.
- Synchronize with the latest base, verify a clean scoped diff, and merge only after every gate passes.
