# Task 01 — Add HTTP and outbound WebSocket modes to the Jinja Render Client

Status: [ ]
Owner: `packages/python/dryv-template-jinja`
Depends on: Task 00 and `dryv-api` Render Client connection task
Validation: protocol conformance, capacity/cancellation/reconnect tests

## Goal

Expose the standalone Jinja renderer through both supported Render Client transport modes while keeping the core renderer transport-independent.

## Modes

1. **HTTP service mode** — expose the shared Render protocol through a reachable render endpoint.
2. **Registered WebSocket client mode** — initiate an outbound persistent connection to `dryv-api`, advertise capabilities, receive render jobs and stream/send RenderResults.

The core render function from Task 00 must be reused by both modes.

## Registration/capabilities

Advertise:

```text
renderer id/version/fingerprint
supported Render protocol/context versions
supported template media/type identifier for Jinja
maximum concurrency/current capacity
determinism/sandbox capability facts required by the protocol
```

## Concurrency

- use bounded worker capacity;
- do not accept unbounded queued jobs from the connection layer;
- update readiness/capacity as jobs start/finish;
- support cancellation before and during render where safely possible;
- maintain stable job IDs and reject duplicate terminal-result emission.

## Transport safety

- validate request size/version before rendering;
- bound output size;
- verify template/context hashes where supplied;
- return structured renderer diagnostics rather than leaking framework tracebacks as protocol success;
- heartbeat/reconnect must not silently repeat completed jobs.

## Non-goals

- Do not add Dryv semantic knowledge.
- Do not write user project files.
- Do not build template context or select templates.

## Allowed paths

- `packages/python/dryv-template-jinja/**`
- `.docs/packages/python/dryv-template-jinja/**`
- shared/generated Render protocol artifacts

## Acceptance criteria

- the same render fixture produces identical content through direct core, HTTP and WS modes.
- outbound WS registration works against test `dryv-api`.
- capacity/backpressure/cancellation are bounded.
- renderer remains independent from Dryv Engine.

## Validation

Test HTTP render, WS registration/job flow, multiple concurrent jobs up to capacity, queue saturation, cancellation, disconnect/reconnect, malformed request and direct-vs-network golden output. Run package tests and `git diff --check`.
