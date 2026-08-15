# Task 03 — Add Render Client HTTP/WS connections

Status: [ ]
Owner: `packages/python/dryv-api`
Depends on: Tasks 00–02 and Dryv Templating/Scheduling tasks
Validation: registration, capability routing, disconnect/retry tests

## Goal

Allow independent Render Clients to participate in builds without being loaded inside Dryv Engine.

Support two transport modes around the same Render protocol:

1. an externally reachable renderer exposed through HTTP;
2. a renderer that initiates an outbound persistent WebSocket connection to `dryv-api` and registers its capabilities.

The second mode is the primary local-user-project pattern because it works through normal outbound connectivity without requiring Dryv to reach a private local port.

## WebSocket registration

Define lifecycle messages equivalent to:

```text
renderer.register
renderer.accepted
renderer.ready
render.request
render.result
render.failed
render.cancel
heartbeat
renderer.draining
renderer.disconnect
```

Registration includes the Render capability/fingerprint contract owned by Dryv Templating protocol.

## HTTP renderer mode

Allow project/server configuration to register a reachable render endpoint whose capabilities/fingerprint can be verified before jobs are sent.

HTTP and WS transports must produce the same logical `RenderSession` contract for Runtime.

## Session registry

`dryv-api` owns transport connection/session lifecycle and exposes established sessions to Runtime with:

```text
stable session id
capabilities/fingerprint
available capacity
project/tenant scope where applicable
send/cancel contract
connection health
```

Runtime/Scheduling decides which compatible session handles a job; `dryv-api` must not perform semantic template selection.

## Security and isolation

- renderer registration must be scoped/authenticated where deployment requires it;
- do not send project resources unrelated to the requested template/context;
- reject protocol/fingerprint changes mid-session unless re-registration occurs;
- bound outstanding jobs per connection;
- heartbeat/disconnect must release capacity and fail/requeue jobs according to Runtime scheduling rules.

## Non-goals

- Do not implement a concrete renderer here.
- Do not build template context here.
- Do not write project files.

## Allowed paths

- `packages/python/dryv-api/**`
- render transport protocol docs/specs
- `.docs/packages/python/dryv-api/**`

## Acceptance criteria

- fake HTTP and WS render services normalize to the same Runtime RenderSession behavior;
- capability/capacity information reaches Scheduling;
- local outbound WS renderer can register and process jobs;
- disconnect/cancellation/heartbeat behavior is bounded and deterministic;
- no renderer-specific semantic code enters `dryv-api`.

## Validation

Test registration, unsupported protocol, capacity routing, HTTP render, WS render, cancellation, heartbeat timeout, reconnect, duplicate result rejection and cross-project isolation. Run package/integration tests and `git diff --check`.
