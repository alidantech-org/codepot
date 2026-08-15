# Task 00 — Build the TypeScript Dryv API client

Status: [ ]
Owner: `packages/nodejs/dryv-client`
Depends on: `dryv-api` Tasks 01–02 and stable API protocol specs
Validation: generated/protocol conformance tests, browser/Node transport tests

## Goal

Create a TypeScript client package that lets VS Code, web apps, playgrounds, desktop apps and other JavaScript frontends use the same Dryv HTTP/WebSocket contracts without importing Dryv Engine.

## Public capabilities

Expose typed operations for:

- API version/capability discovery;
- creating/cancelling/querying builds;
- resource-manifest negotiation;
- uploading missing resource blobs;
- subscribing to build WebSocket events;
- receiving bounded artifact content streams;
- artifact/apply acknowledgements where the frontend has a local writer;
- reconnect/resume using stable IDs when supported.

Types should be generated or verified from the language-neutral API protocol/specification so the TypeScript package cannot silently diverge from the server contract.

## Environment support

Core transport must work in:

```text
browser/web playground
VS Code extension host / Node
Electron/desktop-style JS runtimes
```

Keep environment-specific filesystem/process behavior out of the core transport client.

## Streaming

Handle binary/chunked artifact frames without accumulating all generated files in one giant JSON object. Provide an async iterator/event interface suitable for UI progress and local apply pipelines.

## Error model

Preserve structured Dryv/API diagnostics and distinguish:

```text
protocol error
connection error
build failure
build cancellation
resource upload failure
local apply acknowledgement failure
```

Do not rewrite Runtime semantic errors into generic strings only.

## Non-goals

- Do not add local filesystem writes in this task.
- Do not replicate IR/pack/planning logic.
- Do not execute render/author implementations.

## Allowed paths

- `packages/nodejs/dryv-client/**`
- `.docs/packages/nodejs/dryv-client/**`
- root Node workspace metadata as required
- generated/shared API protocol artifacts

## Acceptance criteria

- one client package works against the same `dryv-api` from browser-compatible and Node test environments.
- HTTP and WS protocol types match the canonical API spec.
- large artifact streams are bounded.
- build cancellation/reconnect/diagnostics are typed.
- no Dryv Engine implementation dependency exists.

## Validation

Use a test `dryv-api` host for build start, resource negotiation/upload, WS progress, artifact streaming, cancellation, reconnect and error cases in Node plus browser-compatible transport tests. Run Node checks and `git diff --check`.
