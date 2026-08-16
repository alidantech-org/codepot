# Task 04 — Bundle and HTTP/WebSocket delivery

Status: [x]
Owner: `packages/python/dryv-api`
Depends on: Task 03

## Goal

Complete the approved stateless V1 server boundary with client-selected stream/bundle delivery and concrete HTTP/WebSocket transport adapters around the already implemented Runtime, preflight, renderer scheduling and artifact-stream operations.

## Delivery modes

Build input now chooses transport delivery only:

```text
stream
bundle
```

This setting does not affect Runtime semantics or `GenerationPlan`.

### Stream

The Project Client observes build events and receives bounded artifact events over:

```text
WS /v1/builds/{buildId}/events
```

Artifact messages preserve stable job/artifact identity, plan index, path, offsets, content hash and dependencies. Content is base64 only at the V1 JSON WebSocket boundary.

A stream-mode Project Client disconnect while rendering cancels the active build so blocked producers/renderers cannot remain indefinitely backpressured by a missing consumer.

### Bundle

Bundle mode consumes the same bounded `ArtifactStream`; it is not a second rendering path.

The server creates one deterministic ZIP containing:

```text
.dryv/manifest.json
<planned generated artifact paths>
```

The manifest records build/plan identity plus artifact path/hash/provenance facts from the plan.

ZIP determinism includes fixed entry order, timestamps, permissions, compression mode and content. Artifacts/final bundles use spooled temporary files so larger builds spill to server temporary storage instead of accumulating in RAM.

The build WebSocket remains the live progress channel while the final ZIP is downloaded over HTTP.

## HTTP transport

`DryvApiServer` is a framework-free ASGI application. The HTTP adapter exposes:

```text
POST   /v1/builds
GET    /v1/builds/{id}
GET    /v1/builds/{id}/plan
POST   /v1/builds/{id}/cancel
GET    /v1/builds/{id}/bundle
DELETE /v1/builds/{id}
```

Build submission includes explicit logical resources with base64 content and optional claimed hashes. Server resource verification still computes the authoritative SHA-256.

ZIP download uses binary HTTP rather than WebSocket/base64 and includes content length plus the deterministic bundle hash as ETag.

## WebSocket transport

Two deliberately separate WebSocket contracts exist:

```text
/v1/builds/{buildId}/events
/v1/renderers
```

The first is Project Client/observer lifecycle and artifact delivery. The second is the external Render Client protocol.

Renderer WebSocket registration starts with `renderer.hello` and advertises renderer identity/version/fingerprint/capabilities/maxConcurrency. The API assigns an opaque connection ID.

Renderer RPC over the socket supports:

```text
template.validate
render.request
render.cancel

template.validation
artifact.begin
artifact.chunk
artifact.end
render.complete
render.failed
```

The WebSocket renderer bridge uses bounded queues. If artifact delivery backpressures the scheduler, renderer inbound queues fill, WebSocket reads slow and transport backpressure propagates toward the Render Client rather than growing memory without bound.

## Server composition/lifecycle

`DryvApiServer` now composes:

```text
BuildManager
DryvRuntime
RendererRegistry
PreflightCoordinator
RenderScheduler
BundleBuilder
HTTP/WebSocket adapters
```

It retains active `RenderExecution` handles so Project Client WebSockets can consume live stream-mode artifacts after build submission returns.

Bundle consumers are attached immediately when bundle-mode rendering begins, preventing the bounded artifact queue from waiting for a later HTTP download.

Release is allowed only after render completion/failure/cancellation, and bundle-mode builds cannot be released while their bundle is still being created.

## Completion evidence

Completed on `develop` without test changes.

- the final approved API ownership tree remains intact;
- old stdio/subprocess/service compatibility paths remain physically absent;
- stream and bundle delivery use the same Runtime/preflight/scheduler execution path;
- HTTP and WebSocket are thin transport adapters and do not reinterpret Canonical IR or packs;
- renderer and Project Client WebSockets are separate protocols;
- artifact streaming and renderer bridges use bounded queues/backpressure;
- deterministic ZIP delivery includes a provenance manifest and spooled storage;
- API/Runtime never write the user's project filesystem;
- direct production-tree inspection found no extra architecture owner;
- transport/scheduler/bundle production files respect the approximately-500-line file ceiling (WebSocket transport is at the ceiling and must not grow without splitting an approved responsibility);
- no tests were created, modified or deleted;
- no test success is claimed; executable certification remains intentionally deferred until user approval.

## Review gate

Stop after this task. Do not begin test work, client work, MCP work, stateful account storage or renderer-specific implementations until the user explicitly approves the final production structure/code.
