---
title: codepotx
description: Complete documentation for the official frontend-neutral TypeScript runtime rewrite.
product: codepotx
package: codepotx
order: 1
---

# `codepotx`

`codepotx` is the official JavaScript runtime rewrite and long-term release line for Codepot.

It stabilizes contract authoring, template compilation, generation planning, safe writes, diagnostics, platform capabilities, and execution behind explicit public boundaries that can be reused by terminals, web applications, editors, MCP servers, and embedded Node.js tools.

## Package status

- workspace package: `codepotx`
- current version: `0.0.0`
- runtime: Node.js 22.18 or newer
- module format: ESM only
- current state: implemented and actively tested in the repository
- public npm stable release: not yet available

Do not present the current workspace package as a completed stable npm release. Its architecture and implemented capabilities are documented so contributors and evaluators can use the current code correctly.

## Public entrypoints

```text
codepotx
codepotx/contract
codepotx/runtime
codepotx/platform
codepotx/authoring
codepotx/templating
codepotx/generation
```

Internal source folders are not supported imports.

## What the runtime owns

- typed authoring and deterministic compiled artifacts;
- template-pack discovery and compilation;
- variable catalogs and reference validation;
- generation plans and in-memory rendering;
- managed manifests, immutable files, stale cleanup, and rollback;
- platform ports and Node/memory adapters;
- typed runtime operations, events, diagnostics, and results.

## Learning path

1. [Evaluate the workspace package](/docs/packages/codepotx/getting-started)
2. [Understand architecture boundaries](/docs/packages/codepotx/architecture)
3. [Author typed contracts](/docs/packages/codepotx/authoring)
4. [Build template packs](/docs/packages/codepotx/templating)
5. [Configure and run generation](/docs/packages/codepotx/generation)
6. [Understand stable artifacts](/docs/packages/codepotx/artifacts)
7. [Use runtime and platform adapters](/docs/packages/codepotx/runtime-platform)
8. [Follow integration best practices](/docs/packages/codepotx/best-practices)

## Ecosystem role

```text
codepot-openapi + codepotg
        ↓ prove behavior in real projects
codepotx
        ↓ stabilize artifacts and runtime operations
Codepot Lang and final platform
```

The mature prototype packages remain supported while `codepotx` reaches release and migration readiness.