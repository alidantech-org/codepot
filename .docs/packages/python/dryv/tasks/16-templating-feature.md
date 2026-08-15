# Task 16 — Build the Templating Feature around Render Sessions

Status: [ ]
Owner: `packages/python/dryv`
Depends on: Tasks 14 and 15
Validation: render-session contract tests, result validation tests, architecture tests

## Goal

Create `features/templating` as the runtime capability that submits already-planned render jobs through an established Render Session and validates the returned artifacts.

The Feature does not execute template engines and does not choose transport/server implementation. Runtime supplies an established session whose capabilities satisfy the planned renderer requirement.

## Render-session contract

Define language-neutral/session-neutral contracts equivalent to:

```text
RenderClientHello / capabilities
RenderRequest
RenderResult
RenderDiagnostic
RenderCancel
```

A Render Request contains at minimum:

```text
protocol version
stable job id
required renderer capability
template resource/content + template hash
canonical JSON context + context hash
planned logical output declarations
render options
```

A Render Result contains at minimum:

```text
job id
renderer fingerprint
logical output id(s)
content bytes/stream
content hash
diagnostics
```

## Renderer capabilities/fingerprint

Capability/fingerprint information must include enough to make scheduling and cache identity safe, such as:

```text
renderer id
renderer version
supported render protocol/context versions
supported template media/type identifiers
helper/extension fingerprint if output-affecting
maximum concurrency or current capacity
determinism declaration where supported
```

The exact wire field names belong to the shared protocol specification; do not make Python types the authority.

## Output safety

Render Clients do not decide arbitrary user-project paths. Planning declares allowed logical output IDs/paths. Templating validates returned logical outputs against that plan.

Default behavior should favor one invocation → one planned artifact, while explicitly declared multi-output templates may return multiple allowed outputs.

Reject:

- unknown output IDs;
- duplicate outputs;
- renderer fingerprint mismatch;
- protocol/version mismatch;
- invalid content hash;
- results for a cancelled/different job.

## Session boundary

The Feature must work with an established session regardless of whether that session is backed by HTTP, WebSocket, local process IPC or another future transport. Network hosting/registration remains outside `dryv`.

## Non-goals

- Do not select templates or build context.
- Do not start/host HTTP or WebSocket servers.
- Do not write project files.
- Do not embed renderer-specific helper APIs inside Dryv IR.

## Allowed paths

- `packages/python/dryv/src/dryv/features/templating/**`
- shared protocol contract representations used by Dryv
- corresponding tests/docs/specs owned by Dryv

## Acceptance criteria

- Dryv can submit a canonical render request through a fake/in-memory Render Session and receive validated artifact content.
- the Feature has no dependency on any concrete template engine.
- renderer fingerprint participates in returned/cached identity.
- returned outputs cannot escape the planned artifact set.
- cancellation and structured renderer diagnostics propagate correctly.

## Validation

Use deterministic fake Render Sessions to test success, multi-output declarations, capability mismatch, malformed results, wrong job IDs, cancellation and diagnostic propagation. Run architecture tests and `git diff --check`.
