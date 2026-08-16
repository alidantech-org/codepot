# dryv-api

`dryv-api` is the network/application host around the transport-neutral `dryv` Runtime.

It receives exact build resources, asks Runtime for a deterministic `GenerationPlan`, coordinates renderer prerequisites and execution, and delivers verified generated artifacts to Project Clients. It does not redefine Canonical IR, pack meaning, selection, context construction or output-path semantics.

## Ownership

```text
Project Client
    │ HTTP / WebSocket
    ▼
dryv-api
    │
    ├── build/resource lifecycle
    ├── DryvRuntime → GenerationPlan
    ├── renderer registry
    ├── template preflight
    ├── renderer capacity scheduling
    ├── bounded artifact streaming
    └── deterministic ZIP delivery
            │
            ▼
       Render Client(s)
```

`dryv-api` owns topology and execution coordination. `dryv` owns semantic planning. Render Clients own template-engine execution. Project Clients own the user's filesystem.

## Build API

The reference ASGI application exposes the current lifecycle through:

```text
POST   /v1/builds
GET    /v1/builds/{build_id}
GET    /v1/builds/{build_id}/plan
POST   /v1/builds/{build_id}/preflight
POST   /v1/builds/{build_id}/render
POST   /v1/builds/{build_id}/cancel
GET    /v1/builds/{build_id}/bundle
DELETE /v1/builds/{build_id}

WS     /v1/builds/{build_id}/events
WS     /v1/renderers
```

Build IDs are route-safe execution identities. They are deliberately separate from semantic `planHash` identity.

## Build inputs

A build request carries:

- the exact `dryv.yaml` bytes;
- Canonical Dryv Runtime IR bytes;
- resolved Template Pack bundles containing manifests and resource bytes;
- explicitly declared additional project resources;
- a delivery mode: `stream` or `bundle`.

The API verifies upload hashes and resource identities before Runtime consumes them. Local paths, Git credentials and source-language authoring execution remain outside the server contract.

## Renderer protocol

Render Clients register over `/v1/renderers` using the versioned renderer-neutral protocol. The logical contract is deliberately small:

```text
renderer.hello
template.validate
render.request
render.cancel

artifact.begin
artifact.chunk
artifact.end
render.complete / render.failed
```

A renderer advertises logical capabilities such as `jinja`, a semantic fingerprint and capacity. Renderer endpoint/connection identity never enters Runtime planning semantics.

Preflight validation is keyed by template hash, context-contract hash and renderer fingerprint. Rendering is dependency-aware and capacity-bounded. Artifact streams are bounded so a slow Project Client naturally applies backpressure instead of causing unbounded server memory growth.

## Delivery

### Stream

Generated artifact begin/chunk/end events are multiplexed with build progress on the Project Client WebSocket. The API validates renderer job/artifact identity, offsets, declared/final sizes and SHA-256 before forwarding completion.

### Bundle

The same bounded artifact stream can instead be consumed by the server's deterministic ZIP builder. ZIP metadata is fixed for reproducibility, large artifacts spill to temporary storage, and `.dryv/manifest.json` records generated artifact identities, paths, sizes and hashes.

There is no second rendering path for bundle mode.

## Cancellation and release

Cancellation propagates from Project Client → API scheduler → active Render Clients and artifact streams. Builds cannot be released while renderer work or bundle packaging is still physically active.

## Local reference topology

The reference `dryv-cli` can host this ASGI application temporarily on loopback and launch the reference Jinja Render Client automatically. An external API can be supplied instead without changing Runtime or pack semantics.

Reference companion implementations live under:

```text
packages/python/dryv-api/.helpers/
├── dryv-author
├── dryv-template-jinja
└── dryv-cli
```
