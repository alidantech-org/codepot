# Task 04 — Bundle and HTTP/WebSocket delivery

Status: [ ]
Owner: `packages/python/dryv-api`
Depends on: Task 03

## Goal

Complete the stateless V1 network host with HTTP build lifecycle, WebSocket progress/control, renderer WebSocket registration and optional deterministic bundle delivery without changing Runtime semantics.

## Delivery modes

Support two API delivery modes:

```text
stream
bundle
```

Delivery mode is an API/client concern, not `dryv.yaml` software meaning.

### Stream mode

Use the bounded artifact streaming path from Task 03.

### Bundle mode

`delivery/bundle.py` packages completed rendered artifacts into a deterministic ZIP-compatible bundle.

`delivery/manifest.py` produces `.dryv/manifest.json` containing at minimum:

- build identity;
- artifact IDs;
- normalized project-relative paths;
- artifact hashes;
- semantic/pack/template provenance available from the plan.

Normalize bundle metadata such as entry ordering and timestamps/permissions where required so identical artifact sets can produce reproducible bundle identity.

Bundle creation belongs only to `dryv-api`.

## HTTP transport

`transport/http.py` owns thin HTTP endpoints for build/resource lifecycle and large bundle download.

Conceptually support:

```text
POST /v1/builds
GET  /v1/builds/{id}
GET  /v1/builds/{id}/plan
POST /v1/builds/{id}/cancel
GET  /v1/builds/{id}/bundle
```

Exact framework/router mechanics may be chosen during implementation, but transport code must call existing build/resource owners rather than contain build logic.

Large bundle bytes should use HTTP download rather than JSON/base64 WebSocket messages.

## WebSocket transport

`transport/websocket.py` owns thin WebSocket framing for two distinct roles:

```text
/v1/builds/{buildId}/events
/v1/renderers
```

Build sockets carry progress, diagnostics, artifact metadata/control and completion events.

Renderer sockets carry the Render Client protocol.

Do not mix UI-specific messages into either protocol.

Bundle mode still streams live build/render/bundle progress over the build WebSocket while artifact bytes are delivered through the bundle download.

## Bundle/client safety

The server emits only normalized project-relative artifact paths. Project Clients must still independently validate downloaded manifest hashes and reject unsafe extraction paths before applying locally.

The API never extracts a bundle into a user project and never receives a user project root for mutation.

## Server composition

`server.py` wires the final components:

```text
DryvRuntime
BuildManager
ResourceStore
RendererRegistry
RendererScheduler
Delivery
HTTP transport
WebSocket transport
```

It must remain a small composition root, not a general service containing the implementation of these owners.

## Stateless V1

No account persistence, shared distributed cache, MCP facade or multi-node coordination is required in this task.

The design must leave room for future content-addressed resource reuse, but do not implement it speculatively.

## Code-size enforcement

Every production source file must remain at or below 500 lines. If a transport file approaches the limit, split by the already approved HTTP/WebSocket responsibility rather than inventing generic services/helpers.

## No-test gate

Do not create, modify or rewrite tests.

## Completion evidence

Before marking complete, inspect production code and demonstrate the intended flow:

```text
Project Client
    → HTTP build request
    → Runtime GenerationPlan
    → renderer prerequisite/preflight/scheduling
    → live WebSocket progress
    → streamed artifacts OR deterministic bundle download
    → Project Client local apply
```

Confirm `dryv-api` contains no project filesystem writer, Runtime contains no network/render execution, no production file exceeds 500 lines and no tests were changed.

After this task, stop for explicit user review of the final production structure/code. Do not begin test implementation until the user explicitly lifts the test gate.
