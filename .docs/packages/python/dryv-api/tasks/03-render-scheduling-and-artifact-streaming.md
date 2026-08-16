# Task 03 — Render scheduling and artifact streaming

Status: [ ]
Owner: `packages/python/dryv-api`
Depends on: Task 02

## Goal

Execute `GenerationPlan` render jobs through connected Render Clients with bounded concurrency, dependency readiness, cancellation, backpressure and live artifact/progress streaming.

## Scheduler ownership

`renderers/scheduler.py` owns execution scheduling only:

- renderer capability matching;
- per-connection capacity;
- bounded outstanding work;
- deterministic eligible-job ordering;
- generation dependency readiness from `GenerationPlan`;
- cancellation propagation;
- renderer disconnect handling;
- backpressure-aware dispatch.

It must not reinterpret pack selectors, context meaning or artifact paths.

## Ordering

Runtime supplies deterministic plan order and dependencies.

Execution may complete concurrently and out of order, but every job/artifact retains:

```text
jobId
artifactId
planIndex
dependencies
```

Arrival timing must never redefine deterministic generation order.

## Artifact streaming

`delivery/streaming.py` owns bounded forwarding of generated artifact data from Render Clients to Project Clients.

Support:

- artifact begin/metadata;
- small inline artifact content when appropriate;
- chunked large artifacts;
- stable offsets/sequence identity;
- artifact completion/hash metadata;
- render/build progress events.

Do not require one whole build to be buffered in memory before clients can receive output.

## Backpressure

Unbounded buffering is forbidden.

Use bounded queues/windows so a slow Project Client eventually slows API consumption from Render Clients. Do not accumulate arbitrary artifact bytes in process memory.

V1 may rely on bounded application queues plus underlying TCP/WebSocket flow control. Explicit credit/window flow control may be added later without changing artifact identity.

## Disconnect policy

Stateless V1 may cancel an active build when the consuming Project Client disconnects if no approved retention mechanism exists.

Do not silently keep unbounded completed output waiting for a client that is gone.

Renderer disconnect/failure must produce explicit API diagnostics and release capacity. Retry behavior, if implemented, must never duplicate a completed artifact identity or violate dependency ordering.

## Build events

WebSocket observers should receive structured events such as:

```text
render.started
render.job.started
render.job.completed
render.progress
artifact.ready
render.completed
build.failed
build.cancelled
```

Messages are data contracts, not UI instructions.

## Code-size enforcement

Every production file must remain at or below 500 lines. Keep scheduling and delivery streaming separate; do not create a large execution service.

## No-test gate

Do not create, modify or rewrite tests.

## Completion evidence

Inspect production code and demonstrate that:

- only ready jobs are dispatched;
- renderer capacity is bounded;
- slow clients cannot create unbounded API buffers;
- artifact/job identity survives concurrent completion order;
- cancellation/disconnect has explicit ownership;
- Runtime contains none of this network execution logic;
- no production file exceeds 500 lines;
- no tests were changed.
