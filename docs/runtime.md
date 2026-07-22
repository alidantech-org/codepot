---
title: Runtime
description: Compose Codepot engines and call typed operations from any frontend.
order: 14
---

# Runtime

```ts
import { createDefaultCodepotRuntime } from 'codepotx/runtime';

const runtime = createDefaultCodepotRuntime({
  projectRoot: process.cwd(),
});

const response = await runtime.execute({
  kind: 'generation.execute',
  input: {
    task: 'sdk',
    codepotFile: { projectRoot: process.cwd() },
  },
});
```

## Operations

The runtime exposes typed authoring, templating, generation, feature, variable-catalog, and context-validation operations.

## Replaceable frontends

CLI, editor integrations, web applications, desktop applications, and test harnesses can all use the same runtime port. Frontends should not parse project configuration, compile contracts, render templates, or write files themselves.

## Custom composition

Use explicit factories to replace platform adapters, import adapters, engines, caches, commands, or event subscribers. Memory services support tests and embedded generation without disk or shell access.
