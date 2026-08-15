# Task 03 — Add local `dryv-api` process lifecycle to CLI

Status: [ ]
Owner: `packages/python/dryv-cli`
Depends on: Tasks 00–02 and `dryv-api` package bootstrap
Validation: local-process lifecycle tests, remote-endpoint bypass tests

## Goal

Make local usage simple without reintroducing in-process Runtime coupling. When configured for local mode, CLI starts or connects to a local `dryv-api` process and then uses the exact same HTTP/WS Project Client flow used for a remote Dryv deployment.

## Local mode

CLI should be able to:

- discover an already-running compatible local `dryv-api` instance;
- otherwise start a child `dryv-api` process using a safe local bind/address strategy;
- wait for version/capability readiness with bounded timeout;
- connect through the normal API client path;
- shut down a CLI-owned child process after terminal completion when appropriate;
- preserve/reuse a long-lived local API instance only through an explicit supported mode.

The CLI must not call Runtime Python methods directly as a local shortcut.

## Remote mode

When an explicit API endpoint is configured, do not start a local server. Use the same resource/build/artifact protocol against the remote host.

## Security

- default local bind must not unintentionally expose the service to external interfaces;
- use per-session/local authentication token or equivalent protection where the API contract requires it;
- do not print sensitive endpoint credentials in normal logs;
- validate API protocol compatibility before sending project resources.

## Renderer/author connections

Local Render Clients/Author Backends may connect outbound to this local API host exactly as they would to a remote API host. CLI does not need to know their implementation details.

Optional future convenience to launch declared local backend/renderer processes must be a separate approved task; do not add hidden process magic here.

## Non-goals

- Do not embed the API server in the CLI process by importing Runtime internals.
- Do not automatically launch arbitrary pack commands/renderers/authors.
- Do not change local file apply behavior.

## Allowed paths

- `packages/python/dryv-cli/**`
- `.docs/packages/python/dryv-cli/**`

## Acceptance criteria

- `dryv generate` can use a child/local API through the same HTTP/WS code path as remote mode.
- remote endpoint mode bypasses local process startup.
- protocol readiness/failure/shutdown are clear and bounded.
- no direct Runtime orchestration path is required.

## Validation

Test existing local API discovery, child startup/readiness, startup failure, incompatible version, clean shutdown, Ctrl+C, remote endpoint bypass and no-engine-import architecture rules. Run CLI tests and `git diff --check`.
