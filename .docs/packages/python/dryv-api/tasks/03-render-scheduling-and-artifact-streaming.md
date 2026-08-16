# Task 03 — Render scheduling and artifact streaming

Status: [x]
Owner: `packages/python/dryv-api`
Depends on: Task 02

## Goal

Execute `GenerationPlan` render jobs through connected Render Clients with bounded concurrency, dependency readiness, cancellation, backpressure and live artifact/progress streaming.

## Implemented scheduler

`renderers/scheduler.py` now owns execution scheduling only:

- consumes Runtime-supplied job order/dependencies;
- dispatches only dependency-ready jobs;
- matches renderer capability from each `RenderJob`;
- refuses renderer fingerprints not approved by preflight;
- reserves/releases per-connection advertised capacity;
- bounds total active render jobs;
- preserves deterministic `jobId`, `artifactId`, plan index and dependency identity regardless of completion timing;
- propagates cancellation to active Render Clients;
- treats disconnected/protocol-failing Render Clients as explicit build failure.

The scheduler never evaluates pack selection or reconstructs template context.

## Artifact protocol validation

Each renderer stream is validated against the exact planned job/artifact:

```text
ArtifactBegin
ArtifactChunk*
ArtifactEnd
RenderComplete
```

The API verifies job/artifact/path identity, chunk offsets, final byte size and SHA-256. Renderer-declared hash/size mismatch is rejected.

## Bounded streaming/backpressure

`delivery/streaming.py` owns `ArtifactStream`, a bounded producer/consumer channel.

- queue length is bounded;
- forwarded chunk size is bounded;
- larger renderer chunks are split into bounded delivery chunks with stable offsets;
- producers block when the Project Client is slower than rendering;
- cancellation drains/unblocks the channel;
- the entire build is never accumulated in process memory for stream delivery.

This allows transport-level TCP/WebSocket backpressure to compose with application-level bounds.

## Live execution

`RenderScheduler.start()` runs coordination in a background thread and returns `RenderExecution` immediately with the live `ArtifactStream`. Project Clients can therefore consume artifacts while other jobs continue rendering.

Build events now include:

```text
render.started
render.job.started
render.job.completed
render.progress
artifact.ready
render.completed
```

## Cancellation ownership

`DryvApiServer.cancel_build()` marks the BuildSession cancelled and asks the scheduler to cancel every active renderer job and artifact stream. Renderer transports receive explicit cancel requests.

## Completion evidence

Completed on `develop` without test changes.

- only dependency-ready jobs are dispatched;
- renderer and global concurrency are bounded;
- only preflight-approved fingerprints may render;
- slow clients backpressure renderer workers through bounded queues;
- artifact identity/order metadata is independent of concurrent completion timing;
- streamed offsets/hash/size are validated by the API;
- cancellation propagates to active Render Clients and blocked streams;
- Runtime contains none of the execution/streaming logic;
- scheduler and streaming modules remain below the 500-line ceiling by inspection;
- no tests were added, modified or deleted.

Task 04 may now add deterministic bundle delivery and concrete HTTP/WebSocket transport adapters around these existing operations/events.
