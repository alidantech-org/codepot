# Task 01 — Connect CLI to Dryv API build and WebSocket streams

Status: [ ]
Owner: `packages/python/dryv-cli`
Depends on: Task 00 and `dryv-api` Tasks 01–02
Validation: HTTP/WS client integration tests, reconnect/cancel tests

## Goal

Replace direct Runtime orchestration with a network Project Client flow. The CLI starts/joins a build through the HTTP API, satisfies missing-resource requests, then follows the build through WebSocket progress/diagnostic/artifact events.

## Required flow

```text
read project resources
→ POST/create build
→ receive missing resource hashes
→ upload missing blobs
→ connect build WebSocket
→ stream progress/diagnostics/artifacts
→ acknowledge artifact receipt/application status
→ receive render/apply terminal state
```

The API endpoint may be local or remote; CLI behavior should be the same apart from connection configuration.

## Client responsibilities

- version/capability handshake before build submission;
- authenticated connection configuration without embedding credentials in project semantic data;
- HTTP resource negotiation/upload;
- WebSocket event decoding;
- bounded artifact-content streaming to the local apply pipeline;
- cancellation on Ctrl+C/user request;
- reconnect/resume using stable build/event IDs where API contract supports it;
- duplicate event/artifact detection;
- clear rendering of Runtime diagnostics without rewriting their meaning.

## Separation

CLI may present progress, tables, JSON, prompts and terminal UX. It must not recalculate semantic selection/planning/cache decisions locally.

CLI must not treat `render_complete` as local success when required artifact application has not completed.

## Non-goals

- Do not implement filesystem apply rules in this task; Task 02 owns them.
- Do not start a local API process automatically yet; Task 03 owns local lifecycle.
- Do not import Runtime internals.

## Allowed paths

- `packages/python/dryv-cli/**`
- `.docs/packages/python/dryv-cli/**`
- shared/generated API protocol artifacts

## Acceptance criteria

- CLI can run against an independently started local or remote `dryv-api` host.
- resources are uploaded only when missing.
- progress/diagnostics/artifact content are streamed incrementally.
- cancellation reaches the server/runtime.
- reconnect/duplicate handling follows the protocol.
- CLI never invokes Dryv Runtime directly in this path.

## Validation

Use an in-process/test API host for successful build, missing-resource upload, remote-style endpoint, cancellation, reconnect, duplicate event, renderer failure and large artifact streaming. Run CLI tests and `git diff --check`.
