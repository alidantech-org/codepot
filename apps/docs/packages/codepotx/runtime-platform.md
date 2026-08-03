---
title: Runtime and platform services
description: Use the frontend-neutral codepotx runtime with Node or memory platform adapters, typed operations, events, cancellation, and source resolution.
product: codepotx
---

# Runtime and platform services

The `codepotx` runtime is the shared application boundary for every frontend. A CLI, web interface, editor extension, MCP server, desktop application, test harness, or embedded Node.js process sends typed requests to the same runtime and receives typed results.

## Create the default runtime

```ts
import { createDefaultCodepotRuntime } from "codepotx/runtime";

const runtime = createDefaultCodepotRuntime({
  projectRoot: process.cwd(),
});

const response = await runtime.execute({
  kind: "generation.plan",
  input: { task: "sdk" },
});
```

The default composition uses production Node platform services and the package-owned authoring, templating, and generation engines.

## Typed runtime operations

Runtime request and response inference is indexed by `RuntimeOperationMap`. An operation kind defines its input, output, diagnostics, and handler contract. Adding a new operation requires an exhaustive handler implementation rather than an untyped switch with unknown payloads.

Operations cover areas such as:

- project validation;
- authoring compilation and inspection;
- template-pack validation;
- variable catalog inspection;
- generation planning;
- generation execution;
- feature and version information.

The exact operation inventory is versioned with the active package. Callers should depend on the public operation map rather than private handlers.

## Runtime lifecycle

A typical request passes through:

```text
validate request
  -> resolve project configuration
  -> resolve sources
  -> call the owning domain port
  -> publish observational events
  -> normalize diagnostics
  -> return a typed response
```

The runtime owns composition and dispatch. It does not move compiler or generator business logic into frontend code.

## Events

Clients can subscribe to lifecycle events for progress presentation, logs, telemetry, or interactive UIs. Event listeners are observational. A listener failure must not alter required operation control flow or turn a successful generation into a failed one.

## Cancellation

Platform cancellation primitives allow a caller to stop long-running source resolution, compilation, planning, rendering, or command execution. Cancellation is returned as a structured operation outcome.

## Platform service contract

Domain layers access external capabilities through `PlatformServices`. They do not import Node filesystem, process, Git, cache, terminal, or clock APIs directly.

The contract includes capabilities such as:

- filesystem and changed-aware writing;
- command execution;
- source resolution;
- TypeScript module loading;
- caching;
- hashing and codecs;
- clocks and identifiers;
- events and cancellation;
- portable path handling;
- transaction support.

## Node adapters

The Node composition provides production adapters for local projects:

- real filesystem access;
- atomic writes;
- child-process commands;
- local and remote source loading;
- TypeScript configuration execution;
- persistent caches;
- Git or package resolution where supported.

Node-specific behavior remains under the platform layer and is not imported by portable domain modules.

## Memory adapters

Memory platform services provide deterministic, side-effect-controlled adapters for tests and embedded use.

```ts
import { createMemoryPlatformServices } from "codepotx/platform";
```

They are useful for:

- unit and integration tests;
- generation previews;
- browser-oriented future adapters;
- isolated examples;
- AI tools that should not receive unrestricted filesystem access.

Node and memory compositions satisfy the same service contract.

## Building another frontend

A new frontend should:

1. load or receive a configured runtime;
2. translate user input into a typed runtime request;
3. subscribe to optional progress events;
4. display the typed response and diagnostics;
5. dispose subscriptions and resources.

It should not reimplement template compilation, generation planning, cleanup, or safety policy.

## Browser direction

A browser-capable platform can provide an in-memory filesystem, Web Worker execution, browser cache, ZIP export, and restricted source adapters. The runtime architecture supports that direction, but browser support should use explicit adapters and supported package entrypoints rather than bundling Node services into the browser.

## Related pages

- [Stable artifacts](/docs/packages/codepotx/artifacts)
- [Generation](/docs/packages/codepotx/generation)
- [codepotx-cli runtime resolution](/docs/packages/codepotx-cli/runtime-resolution)
