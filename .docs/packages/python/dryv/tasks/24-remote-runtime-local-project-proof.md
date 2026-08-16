# Task 24 — Prove remote Runtime with local Project Client ownership

Status: [x]
Owner: `packages/python/dryv`
Depends on: Task 22, `dryv-api`, CLI Project Client tasks
Validation: multi-process integration test with filesystem isolation

> The remote-runtime/local-project proof is implemented on `develop`. Executable/process certification is still pending because the connected repository environment exposes no checkout/test runner. See [`../PROGRESS-18-25.md`](../PROGRESS-18-25.md).

## Goal

Prove the strongest deployment property of the architecture: Dryv Runtime/API may run remotely with no access to the user's project filesystem, while a local Project Client collects resources, receives generated artifacts and safely applies changes.

## Test topology

Run at least three isolated processes/contexts:

```text
A. Project Client / CLI
   owns fixture project directory

B. dryv-api + DryvRuntime
   cannot access fixture project directory

C. Render Client
   separate process/service
```

Author Backend may be added as a fourth process for the author-source variant.

## Required build flows

### Precompiled IR

```text
local project client
→ dryv.yaml + resource manifest + previous managed outputs
→ remote API
→ missing resource negotiation/upload
→ Runtime planning/rendering
→ streamed artifacts/write instructions
→ local atomic apply
→ apply acknowledgements
```

### Author Backend

Repeat using author source + connected Author Backend instead of precompiled IR.

## Filesystem isolation proof

- remote API/Runtime process must have no fixture-project path mounted/accessible;
- no output succeeds through server-side accidental local path access;
- only Project Client changes fixture files;
- absolute client paths never appear as artifact semantic identities;
- private Git credentials/resources remain project-client-side except for resource content explicitly uploaded.

## Failure cases

Test:

- user modifies a managed file before apply;
- Project Client disconnects during artifact streaming;
- renderer disconnects/retries;
- API/Runtime completes rendering but local apply fails;
- resource upload hash mismatch;
- rebuild after partial/failed apply.

Runtime/API must preserve `render_complete` independently from Project Client `apply_complete`.

## Non-goals

- Do not require a real internet deployment; process/container isolation is sufficient if it proves the boundary.
- Do not add cloud-provider-specific code.

## Allowed paths

- cross-package integration test/fixture locations approved for Dryv
- `.docs/packages/python/dryv/**`
- minimal test-only changes in participating packages

## Acceptance criteria

- remote Runtime builds without project filesystem access.
- local Project Client is the only writer/deleter.
- resource/artifact streams are portable and hash-verified.
- local conflicts are refused safely.
- author-source and precompiled-IR flows both work remotely.
- render/apply completion remains distinct under failures.

## Validation

Run the isolated multi-process fixture for successful and failure cases, assert filesystem-access boundaries, verify generated hashes/traces, run architecture tests and `git diff --check`.
