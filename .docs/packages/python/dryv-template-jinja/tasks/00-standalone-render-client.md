# Task 00 — Refactor Jinja package into a standalone Render Client

Status: [ ]
Owner: `packages/python/dryv-template-jinja`
Depends on: Dryv Templating protocol Task 16
Validation: render-protocol conformance tests, no-engine-dependency tests

## Goal

Turn the existing Jinja package into an independent renderer that understands only the shared Render protocol, Jinja template bytes/resources and canonical JSON context.

It must no longer register itself inside Dryv Runtime or import Dryv generation/IR semantics.

## Core render contract

Implement a pure render capability equivalent to:

```text
RenderRequest
    template
    context JSON
    render options
    allowed logical outputs
        ↓
Jinja renderer
        ↓
RenderResult
    output content
    content hash
    renderer fingerprint
    diagnostics
```

The renderer does not select IR concepts, build template context, resolve generated artifact paths, or understand Schema/Operation/Event classes.

## Renderer fingerprint

Fingerprint must include output-affecting identity such as:

```text
renderer id
package/Jinja version
protocol/context version
registered helper/filter/global set and versions
relevant sandbox/configuration version
```

This fingerprint is returned on each result and participates in Dryv render-cache identity.

## Determinism and safety

- use deterministic Jinja environment configuration;
- explicitly register supported filters/globals/helpers;
- sandbox where the existing security design requires it;
- do not expose filesystem/network/process objects through template context;
- reject attempts to emit undeclared logical outputs;
- bound template/context/output sizes according to client configuration.

## Package naming

The current distribution may be renamed later only through an explicit packaging decision. This task changes behavior/ownership first; do not create duplicate renderer implementations merely for a rename.

## Non-goals

- Do not implement HTTP/WS hosting/registration in this task; Task 01 owns transport modes.
- Do not depend on `dryv` Runtime.
- Do not generate template context.
- Do not write user project files.

## Allowed paths

- `packages/python/dryv-template-jinja/**`
- `.docs/packages/python/dryv-template-jinja/**`
- shared/generated Render protocol artifacts

## Acceptance criteria

- renderer can process a canonical RenderRequest without importing Dryv Engine.
- output is returned as RenderResult with content hash/fingerprint.
- context is plain JSON-compatible data.
- current useful deterministic/sandbox behavior is preserved where compatible with the new contract.
- plugin entry-point/runtime registration behavior is no longer required by the core renderer path.

## Validation

Add protocol fixture tests, deterministic golden renders, sandbox/helper tests, malformed request tests, undeclared output rejection and architecture tests proving no Dryv Engine dependency. Run package tests and `git diff --check`.
