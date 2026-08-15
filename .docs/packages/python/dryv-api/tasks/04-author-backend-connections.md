# Task 04 — Add Author Backend HTTP/WS connections

Status: [ ]
Owner: `packages/python/dryv-api`
Depends on: Tasks 00–02 and Dryv Authoring/Scheduling tasks
Validation: registration, IR streaming, disconnect/cancellation tests

## Goal

Allow independent Author Backends to provide Canonical Dryv IR through the same outer service architecture without being imported or executed inside Dryv Engine.

Support two transport modes around the Author Backend protocol:

1. an externally reachable HTTP compile endpoint;
2. an Author Backend that initiates an outbound persistent WebSocket connection to `dryv-api` and registers its capabilities.

Precompiled IR remains the simplest path and requires no Author Backend connection.

## WebSocket registration

Define lifecycle messages equivalent to:

```text
author.register
author.accepted
author.ready
author.request
author.progress
author.ir-record
author.complete
author.failed
author.cancel
heartbeat
author.disconnect
```

Registration includes backend identity/version, supported source kinds, supported IR versions, streaming capability and capacity.

## HTTP backend mode

Allow project/server configuration to register or reference an HTTP Author Backend. HTTP responses must support bounded/streamed Canonical IR output where the implementation allows it rather than forcing huge in-memory JSON responses.

HTTP and WS modes must normalize to the same `AuthorSession` behavior presented to Runtime.

## Source resources

Author source resources are logical Resources already supplied to `dryv-api`. The API sends only the resources/options declared for the author job. Do not give the backend unrestricted server filesystem access.

## Validation boundary

`dryv-api` validates transport/session framing; Dryv Authoring/IR Features validate emitted Canonical IR semantics.

The API must never treat backend-private model objects or arbitrary JSON as canonical merely because transport succeeded.

## Security and isolation

- scope/authenticate backend registrations as required;
- isolate source resources/builds/projects;
- bound outstanding jobs and streamed IR records;
- heartbeat/disconnect releases capacity;
- stable job IDs make retries/deduplication possible;
- do not transmit user Git credentials.

## Non-goals

- Do not implement a specific authoring language here.
- Do not select packs/render templates.
- Do not write project files.

## Allowed paths

- `packages/python/dryv-api/**`
- author transport protocol docs/specs
- `.docs/packages/python/dryv-api/**`

## Acceptance criteria

- fake HTTP and WS author services normalize to one Runtime AuthorSession contract;
- canonical IR records stream through to Dryv validation;
- precompiled IR builds do not require backend registration;
- disconnect/cancellation/progress behavior is bounded;
- backend implementation language is invisible to Runtime/API semantics.

## Validation

Test HTTP compile, WS streaming compile, progress, malformed IR, unsupported IR version, cancellation, disconnect/reconnect, capacity and build isolation. Run package/integration tests and `git diff --check`.
