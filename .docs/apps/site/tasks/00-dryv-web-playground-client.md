# Task 00 — Connect the Dryv web/playground frontend through `dryv-api`

Status: [ ]
Owner: `apps/site`
Depends on: TypeScript `dryv-client` Task 00 and stable `dryv-api` build/artifact stream
Validation: browser integration tests, artifact preview/download tests

## Goal

Use the shared TypeScript Dryv API client for browser-facing Dryv experiences such as the website playground. The frontend must not import/execute Dryv Runtime or assume direct access to a user's local filesystem.

## Browser build flow

Support a flow equivalent to:

```text
user supplies/edits:
    dryv.yaml
    Canonical IR or author source resources
    pack/template resources as permitted by the playground
        ↓
TypeScript dryv-client
        ↓
dryv-api build
        ↓
live progress/diagnostics
        ↓
streamed generated artifacts/write instructions
        ↓
preview / inspect / download / export
```

## Resource handling

Browser resources use logical IDs/content hashes. Do not send fake absolute local paths. Use missing-resource negotiation so repeated unchanged templates/IR need not be resent unnecessarily where the server session/cache supports reuse.

For security, playground packs/templates/authored resources must follow explicit size/type limits and cannot grant arbitrary browser/server filesystem access.

## Artifact behavior

The browser can:

- list planned/generated artifacts;
- show path/content/diff/trace information;
- download individual files or an exported bundle;
- show why an artifact was selected/generated;
- show Runtime diagnostics/progress;
- cancel a build.

The browser must not claim `apply_complete` unless it is actually paired with a trusted local Project Client that reports local application.

## Author/renderer connections

The browser frontend itself does not need to know how Author Backends or Render Clients are implemented. It displays capability/connection diagnostics exposed by the API only where useful.

## Non-goals

- Do not add arbitrary local filesystem writes from the browser.
- Do not replicate IR validation/planning in frontend state.
- Do not embed template engines in the site merely to bypass the Render protocol.

## Allowed paths

- `apps/site/**`
- `.docs/apps/site/**`
- TypeScript Dryv client integration configuration only

## Acceptance criteria

- playground build uses only `dryv-api` through the shared TypeScript client.
- live progress/diagnostics/artifacts stream in the browser.
- artifacts can be previewed/downloaded deterministically.
- no Runtime/engine implementation is bundled into the frontend.
- browser behavior correctly distinguishes render completion from local application.

## Validation

Add browser integration tests for resource upload, build stream, diagnostics, artifact preview/download, cancellation, renderer/backend failure display and reconnect where supported. Run site checks and `git diff --check`.
