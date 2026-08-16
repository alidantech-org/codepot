# Task 02 — Render Client protocol and template preflight

Status: [x]
Owner: `packages/python/dryv-api`
Depends on: Task 01

## Goal

Implement one renderer-neutral protocol for all template engines and perform early template/context compatibility checks before rendering begins.

## Implemented protocol

`renderers/protocol.py` now defines one language-neutral `dryv.render/v1` contract covering:

```text
hello
validate
render
cancel
```

The shared data includes renderer identity/version/fingerprint, capabilities, max concurrency, exact template bytes/hash/media type, canonical context, Runtime context contract, planned output metadata, renderer diagnostics and artifact stream messages.

Render Clients never receive Canonical IR model objects, `dryv.yaml`, pack selectors or generation semantics.

## Connections and registry

`RendererConnection` owns one established Render Client transport plus advertised bounded capacity and lifecycle state.

`RendererRegistry` owns currently connected clients and indexes availability by capability only. Required capabilities are read directly from `GenerationPlan.required_renderers`; the API never reparses pack definitions to rediscover them.

Missing capabilities become API-owned `API_RENDERER_UNAVAILABLE` failures.

## Template preflight

`PreflightCoordinator` validates every currently eligible renderer fingerprint for each planned job before rendering is allowed.

The reusable identity is exactly:

```text
templateHash
+ contextContractHash
+ rendererFingerprint
```

Identical keys validate once within the build preflight. The coordinator retains a `PreflightReport` so later scheduling can prove that the selected renderer fingerprint was actually validated.

Template bytes are retrieved from the same server-verified build ResourceStore referenced by the plan. Hash mismatch between stored bytes and `GenerationPlan` is rejected.

## Build lifecycle

The API build lifecycle now includes:

```text
PLAN_READY
    ↓
PREFLIGHT
    ↓
RENDER_READY
```

`DryvApiServer.preflight_build()` translates renderer/template diagnostics to build diagnostics without changing Runtime meaning.

## Completion evidence

Completed on `develop` without test changes.

- one protocol can represent Jinja, Handlebars and future template engines;
- Render Clients receive template/context/planned-output material only;
- renderer requirements are consumed from `GenerationPlan`;
- bad variables/syntax/helpers can be reported during `validate` before `render` is invoked;
- preflight is renderer-fingerprint aware and cached per build report;
- Runtime imports no renderer connection/session types;
- renderer connection/registry/preflight responsibilities remain separate and below the 500-line ceiling;
- no tests were added, modified or deleted.

Task 03 may now schedule only preflight-approved renderer fingerprints and stream generated artifacts.
