# Task 02 — Implement build WebSocket event and artifact streaming

Status: [ ]
Owner: `packages/python/dryv-api`
Depends on: Task 01 and Dryv Scheduling/Artifacts tasks
Validation: WebSocket protocol tests, backpressure tests, disconnect/cancellation tests

## Goal

Provide a versioned WebSocket build stream so Project Clients can receive progress, diagnostics and generated artifact/write instructions incrementally while the Runtime continues planning/rendering other work.

## Event model

Support stable event categories equivalent to:

```text
build.started
resource.required
authoring.started / progress
planning.started / progress
render.started / completed
artifact.ready
artifact.unchanged
artifact.delete-managed
diagnostic
build.render-complete
build.cancelled
build.failed
```

`apply_complete` must not be emitted merely because Runtime finished rendering. It requires acknowledgement from the Project Client that local artifact application completed successfully.

## Artifact content transfer

Do not embed arbitrarily large generated files into a single JSON WebSocket frame.

Support bounded binary/chunked transfer associated with stable artifact IDs, including:

- artifact metadata before/with content;
- declared content length when known;
- content hash verification;
- ordered chunks per artifact;
- cancellation/abort of incomplete content;
- backpressure when Project Client cannot consume fast enough.

## Session behavior

- reconnect/resume behavior must be explicit and based on stable build/event/artifact IDs;
- duplicate delivery must be detectable/idempotent;
- a disconnected Project Client must not cause unbounded artifact buffering;
- cancellation must propagate to Runtime;
- build success must wait for required Runtime completion, not client UI rendering.

## Project apply acknowledgement

Define an acknowledgement path for Project Clients to report:

```text
artifact applied
artifact refused due to local hash conflict
artifact apply failed
all required artifacts applied
```

The API may then expose `apply_complete` separately from Runtime `render_complete`.

## Non-goals

- Do not perform local project writes on the server.
- Do not register renderer/author service connections in this task.
- Do not redefine Runtime artifact semantics.

## Allowed paths

- `packages/python/dryv-api/**`
- API WS protocol/spec docs
- `.docs/packages/python/dryv-api/**`

## Acceptance criteria

- a client can observe a build and receive artifacts progressively;
- large artifacts stream with bounded memory;
- slow clients apply backpressure;
- disconnect/cancel paths terminate cleanly;
- `render_complete` and `apply_complete` are distinct states;
- local apply conflicts can be reported without pretending the build was applied.

## Validation

Add tests for ordered progress, multi-artifact concurrent production, slow consumer, reconnect/idempotency behavior, binary chunk verification, cancellation, local apply failure acknowledgement and separate render/apply completion. Run package/integration tests and `git diff --check`.
