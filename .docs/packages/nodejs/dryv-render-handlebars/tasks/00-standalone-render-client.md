# Task 00 — Build the Node.js Handlebars Render Client

Status: [ ]
Owner: `packages/nodejs/dryv-render-handlebars`
Depends on: Dryv Templating protocol Task 16
Validation: protocol conformance tests, deterministic render fixtures

## Goal

Create a Node.js Render Client using Handlebars as the first proof that Dryv template execution is independent from the Python engine process.

The package understands only the shared Render protocol, Handlebars template content and canonical JSON context.

## Core render contract

Implement a transport-independent render function equivalent to:

```text
RenderRequest
    template bytes/text
    canonical JSON context
    render options
    allowed logical outputs
        ↓
Handlebars
        ↓
RenderResult
    logical output id(s)
    content bytes
    content hash
    renderer fingerprint
    diagnostics
```

It must not import or replicate Dryv IR semantic models.

## Renderer fingerprint

Fingerprint must include output-affecting identity including:

```text
renderer id
package/Handlebars version
Render protocol/context version
registered helper set and versions
relevant renderer configuration
```

## Determinism and helper policy

- register helpers explicitly;
- helper behavior affecting output participates in fingerprinting;
- do not expose filesystem/network/process capabilities through template context;
- deterministic input must produce deterministic bytes;
- validate allowed output IDs;
- bound request/template/context/output sizes.

## Package integration

Add the package under the existing root Node.js workspace conventions. Do not make Python installation/imports a requirement.

## Non-goals

- Do not add HTTP/WS transport modes until Task 01.
- Do not build Dryv template context.
- Do not select packs/templates.
- Do not write user project files.

## Allowed paths

- `packages/nodejs/dryv-render-handlebars/**`
- `.docs/packages/nodejs/dryv-render-handlebars/**`
- root Node workspace metadata only as required
- shared/generated Render protocol artifacts

## Acceptance criteria

- package installs/tests independently in Node workspace.
- canonical RenderRequest fixtures produce valid RenderResults.
- no Python/Dryv Engine dependency exists.
- fingerprint/hash behavior is deterministic.
- helper policy is explicit and testable.

## Validation

Add golden render tests, helper/fingerprint tests, malformed request tests, output-ID validation and deterministic repeated-run tests. Run Node package checks and `git diff --check`.
