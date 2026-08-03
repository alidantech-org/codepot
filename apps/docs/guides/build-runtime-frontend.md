---
title: Build a runtime frontend
description: Integrate codepotx into a CLI, web application, editor, MCP server, desktop tool, or embedded Node.js workflow.
order: 43
---

# Build a runtime frontend

A `codepotx` frontend translates user intent into runtime requests and presents runtime responses.

It should not duplicate domain logic from authoring, templating, generation, or platform layers.

## 1. Use a public runtime entrypoint

```ts
import { createDefaultCodepotRuntime } from 'codepotx/runtime';
```

Do not import internal source folders.

## 2. Create one runtime for the project context

```ts
const runtime = createDefaultCodepotRuntime({
  projectRoot,
});
```

A long-lived UI may keep the runtime for repeated operations while respecting cache refresh and cancellation options.

## 3. Send typed requests

```ts
const response = await runtime.execute({
  kind: 'generation.plan',
  input: {
    task: 'sdk',
  },
});
```

Use runtime contracts for validation, variable discovery, plan creation, dry runs, generation, and inspection.

## 4. Present structured responses

Do not reduce every operation to printed text inside the engine.

A web UI may show files grouped by outcome. An editor may open diagnostics and diffs. An MCP tool may return a concise structured payload. The runtime result should remain the shared source.

## 5. Subscribe to events

Events can power progress displays and logs. They are observational: listener failures must not alter required generation control flow.

Dispose subscriptions when a command, request, or UI session ends.

## 6. Support cancellation

Pass cancellation through the runtime instead of stopping only the presentation layer. The engine checks cancellation between major stages and rolls back transactional work when cancellation arrives after mutation.

## 7. Keep platform access injected

Use provided Node or memory platform services, or implement existing public ports for another environment.

Do not place filesystem, process, Git, cache, or terminal calls inside domain code.

## 8. Follow `codepotx-cli`

The CLI package is the reference separation:

```text
arguments → runtime loader → typed execution → presenter → exit code
```

New frontends should add presentation and interaction, not a second compiler or generator.
