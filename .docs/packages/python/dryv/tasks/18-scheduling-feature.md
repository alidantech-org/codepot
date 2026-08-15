# Task 18 — Build the Scheduling Feature

Status: [ ]
Owner: `packages/python/dryv`
Depends on: Tasks 14–17
Validation: concurrency/backpressure/cancellation tests

## Goal

Create `features/scheduling` as the single owner of bounded concurrent build work. Planning defines graph readiness; Scheduling decides when ready context/render/artifact jobs run and how capacity/backpressure/cancellation propagate.

## Required queues/stages

Model bounded work for at least:

```text
context preparation/cache resolution
render jobs
render results
artifact delivery
event/progress delivery
```

Author Backend work may also be scheduled when a build requires authored source compilation.

Queues must be bounded. A slow renderer, client stream or backend must apply backpressure instead of allowing unbounded memory growth.

## Readiness and dependencies

- use planned dependency graph readiness, not a global "render everything then write" barrier;
- independent artifacts may render concurrently;
- an artifact may render before a dependency is physically applied when its virtual path/symbol facts are already known;
- true content-dependent/aggregate outputs wait only for required upstream results;
- preserve deterministic final artifact ordering/identity even when execution completion order differs.

## Capacity

Scheduling must account for session capabilities such as maximum concurrency/current capacity. It may distribute independent work across several compatible Render Sessions.

Do not assume more sessions always means faster. Keep dispatch overhead bounded and support batching only when the protocol later explicitly provides it.

## Cancellation/failure

Define clear propagation for:

- build cancellation;
- per-job cancellation;
- renderer/backend disconnect;
- timeout;
- non-retryable renderer error;
- retry-safe transport failure;
- artifact-delivery backpressure.

A build must not report success while required queues/results are unresolved or failures are pending.

## Non-goals

- Do not select templates or build dependency graphs here.
- Do not manage network WebSocket connection lifecycle.
- Do not write user files.
- Do not own cache-key semantics.

## Allowed paths

- `packages/python/dryv/src/dryv/features/scheduling/**`
- current queue/execution scheduling modules being migrated where owned by this capability
- corresponding tests/docs

## Acceptance criteria

- queues are bounded and demonstrably apply backpressure;
- independent jobs use available renderer capacity concurrently;
- dependency readiness is honored;
- cancellation/failure propagates and drains/terminates safely;
- deterministic artifact identity/order is independent from concurrent completion order.

## Validation

Use fake slow/fast renderer sessions to test saturation, capacity limits, fair dispatch, cancellation, timeout, disconnect/retry safety, dependency readiness and deterministic results. Run architecture tests and `git diff --check`.
