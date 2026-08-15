# Task 23 — Prove heterogeneous renderers, concurrency, and incremental cache

Status: [ ]
Owner: `packages/python/dryv`
Depends on: Task 22, Jinja Render Client, Handlebars Render Client
Validation: multi-process integration tests, cache invalidation assertions, scheduler/backpressure tests

## Goal

Prove that one Dryv build can use several independent Render Clients concurrently and still preserve deterministic planning, cache correctness and artifact output.

## Multi-renderer fixture

Use one project/IR/pack set where independent template invocations require at least:

```text
Jinja renderer
Handlebars renderer
```

The Render Clients must run as separate processes/services through the shared Render protocol. Dryv Engine must not import either implementation.

## Concurrency proof

Demonstrate:

- independent render jobs are dispatched concurrently when dependency graph and renderer capacity permit;
- planning/context construction can continue while earlier render jobs are in flight;
- virtual artifact paths allow dependent import/path planning before physical local apply;
- bounded queues apply backpressure when one renderer is intentionally slow;
- output ordering/identity remains deterministic regardless of completion timing.

## Cache proof

Run controlled changes and verify minimal invalidation:

### No change

- context cache hit where applicable;
- render cache hit;
- artifacts classified unchanged;
- no unnecessary renderer call.

### Change unrelated Schema

- artifacts whose context did not consume that branch remain cached.

### Change relevant nested/base Schema

- dependent context/render entries invalidate;
- unrelated outputs remain reusable.

### Change template

- only invocations using that template rerender.

### Change renderer fingerprint/version/helper set

- affected render-cache entries invalidate even with identical template/context hashes.

### `refresh`

- recompute requested stages according to cache contract and replace valid cache entries after success.

### `off`

- no cache read/write.

## Failure safety

A renderer failure/cancellation must not commit a false successful cache state. Previously valid entries must remain coherent.

## Non-goals

- Do not benchmark remote internet rendering as inherently faster.
- Do not add renderer-specific code to Dryv.
- Do not change pack semantics solely for the test.

## Allowed paths

- Dryv integration/performance tests and fixtures
- test/config fixtures in Jinja/Handlebars clients
- `.docs/packages/python/dryv/**`

## Acceptance criteria

- one build successfully uses at least two renderer implementations.
- concurrency is bounded and observable.
- cache invalidation follows exact context/template/renderer dependencies.
- deterministic final output is independent of execution timing.
- failure/cancellation does not poison cache.

## Validation

Record renderer call counts, context/render cache hits/misses, queue saturation behavior, artifact hashes and deterministic repeated-build output across all change cases. Run architecture tests and `git diff --check`.
