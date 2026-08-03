---
title: Architecture
description: Understand the shared project principles and the different architectures used by the prototype, JavaScript, and Rust generations.
order: 5
---

# Architecture

Codepot uses different implementations at different maturity stages, but the project follows one architectural direction: separate software meaning, generation policy, platform capabilities, and user interfaces.

## Shared conceptual layers

```text
software intent
    ↓
validated semantic or normalized artifact
    ↓
target-specific template/render model
    ↓
complete generation plan
    ↓
safe project-owned writes
```

The exact files and engines differ, but the boundaries remain recognizable.

## Prototype architecture

```text
codepot-openapi TypeScript builders
        ↓
OpenAPI 3.x + x-codegen metadata
        ↓
codepotg OpenAPI loader and inference
        ↓
normalized generation contracts
        ↓
Jinja template pack + paths.yaml
        ↓
planned files, lifecycle policy, diagnostics, writes
```

OpenAPI is the interchange boundary. This makes the authoring and generation packages independently useful.

## `codepotx` architecture

`codepotx` communicates through versioned, readonly, JSON-safe artifacts:

- compiled authoring artifact;
- compiled template pack;
- template variable catalog;
- generation plan;
- rendered generation;
- generation manifest;
- generation result.

Its public areas are:

```text
contract
internal
authoring
templating
generation
platform
runtime
```

The runtime composes engines through ports. Node and memory platform adapters satisfy the same service contract. The CLI imports public runtime and contract APIs instead of internal folders.

Read [`codepotx`](/docs/codepotx) for the package-level dependency rules.

## Final Rust architecture

```text
Codepot.toml + source modules
    ↓
filesystem package resolver + std selection
    ↓
lossless lexer + recoverable parser
    ↓
package/import graph + symbols + strong semantic analysis
    ↓
target-neutral IR + persistent workspace snapshot
    ↓
CLI | LSP | extension | future runtime/generators | web | MCP
```

The compiler owns meaning. Future generators consume resolved IR rather than re-deciding types, validation, imports, or security inside templates.

## Frontend-neutral execution

A central rule for both `codepotx` and the final platform is that interfaces do not own engine behavior.

```text
terminal  editor  web  MCP  desktop  AI agent
     \      |      |    |      |       /
          reusable runtime and artifacts
```

This keeps behavior consistent across tools and makes it possible to add new interfaces without rebuilding the compiler or generator.

## Safety boundaries

- Plan complete output before mutation.
- Keep generated ownership explicit.
- Preserve immutable and user-edited files.
- Restrict cleanup to known managed files and allowed scopes.
- Keep diagnostics structured and available to every frontend.
- Treat commands and filesystem access as injected platform capabilities rather than domain logic.
