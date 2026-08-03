---
title: Runtime architecture
description: Understand codepotx package boundaries, dependency direction, ports, adapters, and composition.
product: codepotx
package: codepotx
order: 3
---

# Runtime architecture

`codepotx` is organized around stable contracts and dependency direction rather than one command-line implementation.

## Layers

```text
contract
  versioned protocols, artifacts, operations, ports, diagnostics, events, sources

internal
  package metadata, portable paths, shared operation results

authoring
  typed DSL domains, compiler passes, normalization, validation, source loading

templating
  paths.yaml, discovery, descriptors, references, variables, Handlebars rendering

generation
  CodepotFile.yml, planning, rendering, manifests, transactions, commands, reports

platform
  Node adapters, memory adapters, cancellation, codecs, hashing, events, source resolution

runtime
  typed requests, exhaustive dispatch, lifecycle events, composition
```

## Dependency direction

Domain layers depend on contracts and ports, not concrete filesystem, process, Git, cache, or terminal implementations.

```text
frontend
   ↓ runtime operations
runtime
   ↓ authoring / templating / generation ports
engines
   ↓ platform service ports
Node or memory adapters
```

Architecture tests enforce these boundaries.

## Contract layer

`codepotx/contract` contains readonly, JSON-safe public types for:

- compiled artifacts;
- runtime operations;
- diagnostics and events;
- source descriptors;
- platform and engine ports;
- generation plans and results.

This layer must remain portable and free from implementation objects.

## Authoring layer

The authoring engine:

- loads local or configured source;
- executes the typed DSL;
- normalizes registries;
- validates references and invariants;
- emits `CompiledAuthoringArtifact`.

## Templating layer

The templating engine:

- resolves template-pack sources;
- discovers templates, partials, and raw files;
- compiles `paths.yaml`;
- validates helpers, references, selectors, and output paths;
- builds `CompiledTemplatePack` and `TemplateVariableCatalog`.

## Generation layer

The generation engine:

- loads `CodepotFile.yml`;
- compiles sources;
- validates context requirements;
- plans files, commands, and cleanup;
- renders in memory;
- applies transactions and manifests;
- emits reports and diagnostics.

## Platform layer

`PlatformServices` supplies capabilities through ports:

- filesystem and changed-aware writes;
- commands and environment;
- TypeScript module loading;
- local/package/Git/artifact/memory sources;
- hashing, codecs, paths, IDs, and clocks;
- cancellation and events;
- cache storage.

## Runtime layer

The runtime maps a typed request kind to one handler and typed result. Frontends subscribe to observational events and call `execute`.

Adding a runtime operation requires updating the operation map and providing the matching handler. This keeps dispatch exhaustive.

## Frontend rule

A frontend may:

- parse user input;
- construct runtime requests;
- subscribe to events;
- present results and diagnostics.

It must not reimplement compiler, planner, writer, manifest, or cleanup behavior.

## Why this matters

The same engine can power:

- `codepotx-cli`;
- an editor extension;
- a web playground;
- an MCP server;
- a desktop tool;
- an in-memory test harness;
- another Node.js application.

Shared operations keep behavior consistent across every frontend.