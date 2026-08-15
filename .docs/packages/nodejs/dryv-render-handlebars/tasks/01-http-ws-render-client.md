# Task 01 — Add HTTP and outbound WebSocket modes to the Handlebars Render Client

Status: [ ]
Owner: `packages/nodejs/dryv-render-handlebars`
Depends on: Task 00 and `dryv-api` Render Client connection task
Validation: HTTP/WS protocol conformance, concurrency/cancellation tests

## Goal

Expose the Handlebars core renderer through both supported Render Client transport modes while preserving one transport-independent render implementation.

## Modes

1. **HTTP service mode** — expose a versioned render endpoint implementing the shared Render protocol.
2. **Registered WebSocket client mode** — connect outbound to `dryv-api`, register renderer capabilities, receive render jobs and return results.

## Registration

Advertise:

```text
renderer id/version/fingerprint
supported Render protocol/context versions
Handlebars template media/type identifier
maximum concurrency/current capacity
output-affecting helper/configuration fingerprint
```

## Concurrency and backpressure

- bounded work queue;
- explicit max concurrency;
- update ready/capacity state as jobs run;
- reject/defer work when saturated rather than buffering without limit;
- support cancellation;
- stable job IDs prevent duplicate terminal results.

## HTTP behavior

HTTP mode must support bounded body/context/template sizes and structured errors. It must return the same logical RenderResult as WebSocket/direct rendering for the same request.

## WebSocket behavior

Implement registration, heartbeat, request/result/error/cancel and clean disconnect/re-registration semantics compatible with `dryv-api`.

The Render Client initiates the connection; the user's machine does not need to expose an inbound local renderer port for the WS mode.

## Non-goals

- Do not add Dryv IR models.
- Do not build context or choose templates.
- Do not mutate project files.

## Allowed paths

- `packages/nodejs/dryv-render-handlebars/**`
- `.docs/packages/nodejs/dryv-render-handlebars/**`
- shared/generated Render protocol artifacts

## Acceptance criteria

- direct, HTTP and WS modes produce identical output for golden requests.
- renderer registers and advertises capacity correctly.
- backpressure/cancellation/reconnect behavior is bounded.
- package remains independent from Python/Dryv Engine.

## Validation

Test HTTP render, WS registration and render jobs, saturation, cancellation, heartbeat timeout, reconnect/idempotency, malformed requests and golden output equivalence. Run Node checks and `git diff --check`.
