# Task 00 — Bootstrap `dryv-api` as the Dryv Runtime network host

Status: [ ]
Owner: `packages/python/dryv-api`
Depends on: Dryv Task 20 — Runtime composition
Validation: package tests, in-process API tests, import-boundary tests

## Goal

Create a separate `dryv-api` package that hosts `DryvRuntime` behind versioned HTTP/WebSocket contracts. Networking is outside the Dryv Engine; this package is the transport/service boundary used by local or remote frontends and by connected Author/Render clients.

## Package responsibilities

`dryv-api` owns:

- process/server lifecycle;
- HTTP routing;
- WebSocket routing;
- API authentication/authorization hooks without defining project business policies;
- build-session identity/lifecycle;
- transport-level cancellation;
- resource upload/download/stream framing;
- progress/diagnostic/artifact streaming;
- connected Author Backend session registration;
- connected Render Client session registration;
- translation between wire messages and public Dryv Runtime contracts.

`dryv-api` must not reimplement IR validation, pack planning, context generation, caching, scheduling or artifact classification.

## Dependency direction

```text
dryv-api → dryv public Runtime/API contracts

dryv ✗→ dryv-api
```

Frontends should not need to import `dryv` directly when using network mode.

## Protocol authority

Define/version HTTP/WS schemas in language-neutral specifications. Framework request/response classes are generated/transport representations, not the protocol authority.

Use an implementation-appropriate ASGI stack after inspecting repository conventions. Framework choice must not leak into Dryv Runtime or shared protocol semantics.

## Initial endpoints/capabilities

Bootstrap only health/version/capability and build-session skeletons needed by later tasks. Do not implement full build/resource/artifact behavior until Tasks 01–04.

## Non-goals

- Do not mutate user project files.
- Do not execute templates or author source inside this package.
- Do not copy Runtime logic.
- Do not embed CLI/VS Code/web UI behavior.

## Allowed paths

- `packages/python/dryv-api/**`
- `.docs/packages/python/dryv-api/**`
- shared protocol specification files explicitly owned by the API contract
- root workspace metadata only as required to add the package

## Acceptance criteria

- `dryv-api` is an independent workspace package.
- it can host a supplied `DryvRuntime` and expose version/capability health endpoints.
- no reverse dependency from `dryv` exists.
- HTTP/WS transport models are isolated from canonical IR/runtime semantics.
- architecture tests detect forbidden cross-package imports.

## Validation

Run isolated package tests through the root workspace, an in-process API smoke test, import-boundary tests and `git diff --check`.
