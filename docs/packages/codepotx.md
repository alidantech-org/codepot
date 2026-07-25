---
title: codepotx
description: The official frontend-neutral JavaScript runtime and stable rewrite of the Codepot authoring, templating, and generation model.
product: codepotx
order: 12
---

# `codepotx`

`codepotx` is the official JavaScript rewrite and long-term supported release line for Codepot.

It stabilizes ideas proven through `codepot-openapi`, `codepotg`, and real projects into a coherent runtime with explicit contracts, strict architecture boundaries, deterministic artifacts, safe generation, and support for multiple user interfaces.

## Current status

The package is under active development in the monorepo and currently has workspace version `0.0.0`. It should be described as the official stable rewrite—not as an already completed public stable release.

Registry links remain marked as TBD until publication is ready.

## Core model

`codepotx` combines three independently reusable inputs:

1. **Authoring source** — normally `codepotx.config.ts`.
2. **Template pack** — Handlebars files plus `paths.yaml`.
3. **Consumer task** — `CodepotFile.yml`, controlling sources, output, variables, commands, and cleanup policy.

```text
codepotx.config.ts
        +
Handlebars template pack
        +
CodepotFile.yml
        ↓
compile → validate → plan → render → safe write → report
```

## Public entrypoints

```ts
import { defineVersionContract, defineResource, schema, z } from 'codepotx';
import type { CompiledAuthoringArtifact } from 'codepotx/contract';
import { DefaultAuthoringCompiler } from 'codepotx/authoring';
import { createTemplatingEngine } from 'codepotx/templating';
import { createGenerationEngine } from 'codepotx/generation';
import { createMemoryPlatformServices } from 'codepotx/platform';
import { createDefaultCodepotRuntime } from 'codepotx/runtime';
```

Supported package subpaths are explicit:

```text
codepotx
codepotx/contract
codepotx/authoring
codepotx/templating
codepotx/generation
codepotx/platform
codepotx/runtime
```

Internal source folders are not public package entrypoints.

## Architecture

```text
contract
  versioned protocol, artifacts, operations, ports, diagnostics, events

internal
  portable paths, package metadata, shared operation results

authoring
  DSL domains, compiler passes, validation, source and cache infrastructure

templating
  config normalization, discovery, descriptors, paths, variables, rendering

generation
  task config, planning, rendering coordination, writes, manifests, reports

platform
  Node, memory, and shared capability adapters

runtime
  run context, typed dispatch, lifecycle events, and composition
```

Architecture tests enforce dependency direction. Authoring and templating do not import generation. Generation depends on authoring and templating ports rather than concrete implementations. Domain layers do not call un-injected filesystem, process, Git, cache, or terminal APIs.

## Stable artifacts

The layers communicate through readonly, JSON-safe artifacts such as:

- `CompiledAuthoringArtifact`;
- `CompiledTemplatePack`;
- `TemplateVariableCatalog`;
- `GenerationPlan`;
- `RenderedGeneration`;
- `GenerationManifest`;
- `GenerationResult`.

Artifacts do not contain mutable builders, runtime Zod or Handlebars objects, CLI presentation state, or platform implementations.

## Authoring

```ts
import { defineCodepotConfig, defineVersionContract, z } from 'codepotx';

const v1 = defineVersionContract({
  info: { title: 'Example', version: '1.0.0' },
});

const schemas = v1.defineSchemas({
  User: {
    id: z.string().uuid(),
    name: z.string().min(1),
  },
});

const users = v1.defineResource({
  name: 'users',
  route: '/v1/users',
});

users.defineRoutes()
  .params(schemas.ref.User.pick({ id: true }))
  .routes((route) => ({
    listUsers: route.get('/').response(schemas.ref.User.array()),
    updateUser: route.patch('/:id')
      .body(schemas.ref.User.partial())
      .response(schemas.ref.User),
  }));

export default defineCodepotConfig({ contracts: [v1] });
```

Fields are selectable and editable by default. `.immutable()` allows create-time assignment but blocks updates. `.managed()` marks backend ownership and readonly behavior.

## Template packs

A template pack owns framework conventions, output structure, filenames, imports, static files, partials, naming, selections, and lifecycle policy.

Compilation separates raw YAML, normalized config, discovery, descriptors, references, context, variable introspection, and secure Handlebars rendering.

Prototype access is disabled and unknown required variables fail before rendering.

## Generation safety

Generation resolves and validates the complete plan before mutation.

Dry runs do not write files or execute commands. Managed, immutable, protected, refused, stale cleanup, atomic write, cancellation, command failure, and rollback behavior are explicit runtime results.

Read [Generation safety](/docs/generation-safety) for the common guarantees.

## Runtime

```ts
import { createDefaultCodepotRuntime } from 'codepotx/runtime';

const runtime = createDefaultCodepotRuntime({
  projectRoot: process.cwd(),
});

const response = await runtime.execute({
  kind: 'generation.execute',
  input: { task: 'sdk' },
});
```

Runtime operations use an exhaustive typed handler registry. Adding an operation requires a matching request/result pair and handler.

Events are ordered and observational. Listener failures cannot change required control flow.

## Multiple frontends

The runtime can serve:

```text
codepotx-cli
web applications
editor extensions
MCP servers
internal developer portals
desktop tools
embedded Node.js applications
```

Frontend code should translate user input into runtime requests and present runtime responses. It should not reimplement planning, compilation, generation, or safety decisions.

## Relationship to the prototypes

`codepot-openapi` and `codepotg` remain supported and provide production evidence for features moving into this package.

The goal is not to copy every old implementation. The goal is to stabilize verified semantics and safety guarantees behind clearer runtime boundaries.

## Validation

```bash
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
pnpm --filter codepotx package:lint
pnpm --filter codepotx check
```

The package is ESM-only and requires Node.js 22.18 or newer.
