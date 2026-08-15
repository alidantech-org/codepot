# Task 01 — Implement build and resource HTTP APIs

Status: [ ]
Owner: `packages/python/dryv-api`
Depends on: Task 00 and Dryv Resources/Project/Runtime tasks
Validation: API contract tests, content-addressed upload tests, Runtime integration tests

## Goal

Expose the HTTP portion of the Dryv build protocol for creating builds, supplying project resources, querying build state, cancelling builds and retrieving completed artifact metadata/content when streaming is not used.

## Build start

A Project Client must be able to submit a build request containing or referencing:

```text
dryv.yaml
resource manifest
previous managed-output manifest
cache mode
build mode
project bindings/options allowed by dryv.yaml
```

The server normalizes transport data into public Dryv Runtime input contracts. It does not interpret generation semantics itself.

## Content-addressed resource flow

Support an efficient two-step resource flow:

```text
client sends resource manifest/hashes
server reports missing content hashes
client uploads only missing resources
```

Resources may include:

```text
serialized IR
pack manifests
template files
author source resources
other explicitly declared project resources
```

The API must preserve logical resource IDs and content hashes without depending on the client's absolute filesystem paths.

## HTTP capabilities

Provide versioned operations equivalent to:

```text
create build
query build state
supply/query missing resources
cancel build
list artifact metadata
fetch artifact content when available
```

Exact URL names are part of the API contract and must be documented/tested consistently rather than inferred from these conceptual names.

## Safety

- enforce resource size/count limits and streaming uploads;
- reject mismatched content hashes;
- reject path traversal in logical resource names;
- isolate resources by build/project/session scope;
- never accept raw local filesystem paths as authority;
- do not accept user Git credentials into Dryv resource contracts.

## Non-goals

- Do not implement live progress/artifact streaming; WebSocket task owns it.
- Do not register Render/Author connections here.
- Do not write generated project files.

## Allowed paths

- `packages/python/dryv-api/**`
- API protocol/spec docs owned by `dryv-api`
- `.docs/packages/python/dryv-api/**`

## Acceptance criteria

- a Project Client can start a build and satisfy missing resource requests through content hashes;
- Runtime receives the exact logical resources/configuration after transport normalization;
- build cancellation reaches Runtime;
- large resource uploads are bounded/streamed;
- invalid hashes/resource identities are rejected with stable diagnostics.

## Validation

Add API tests for minimal build, missing-resource negotiation, duplicate resource reuse, corrupted upload, cancellation and artifact retrieval. Run root-workspace tests for `dryv-api`, Dryv integration tests and `git diff --check`.
