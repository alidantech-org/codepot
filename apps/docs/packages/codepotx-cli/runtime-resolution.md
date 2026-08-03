---
title: Project-local runtime resolution
description: Learn why codepotx-cli loads the consumer project's codepotx/runtime and how that keeps terminal behavior aligned with project dependencies.
product: codepotx-cli
---

# Project-local runtime resolution

For normal project commands, `codepotx-cli` prefers the consumer project's local `codepotx/runtime` installation. The CLI should not embed a second independent copy of compiler and generator behavior.

## Resolution flow

```text
resolve project root
  -> locate project-local codepotx package
  -> load supported codepotx/runtime entrypoint
  -> create or obtain the project runtime
  -> subscribe to lifecycle events
  -> execute a typed operation
  -> dispose subscriptions
  -> map the result to terminal or JSON output
```

This keeps the frontend aligned with the runtime version chosen by the project lockfile.

## Why this matters

Without project-local resolution, a globally installed CLI could silently run a different compiler, artifact schema, template engine, or generation policy from the version declared by the project.

Project-local resolution provides:

- reproducible behavior across developer machines;
- compatibility with the project's lockfile;
- one domain implementation for CLI and programmatic use;
- safer upgrades;
- clearer version diagnostics.

## Supported package boundaries

The CLI loads the published runtime entrypoint:

```ts
import { createDefaultCodepotRuntime } from "codepotx/runtime";
```

It must not import private runtime handlers or internal source files from the consumer project.

## Explicit project paths

Use explicit paths when the command is launched outside the project root:

```bash
codepotx validate \
  --root /workspace/acme \
  --file /workspace/acme/CodepotFile.yml \
  --config /workspace/acme/codepotx.config.ts
```

The CLI passes these values into runtime resolution. It does not interpret contract or task semantics itself.

## Version and compatibility failures

A clear failure should be returned when:

- `codepotx` is not installed in the project;
- the runtime entrypoint is unavailable;
- the CLI and runtime operation contracts are incompatible;
- the project requires a newer feature than the loaded runtime provides;
- an unsupported private entrypoint is referenced.

Do not fall back silently to unrelated global engine behavior.

## Embedded use

Applications that do not need terminal parsing can call the runtime directly. The CLI also exposes a programmatic entrypoint for terminal-compatible invocation:

```ts
import { runCli } from "codepotx-cli";

const exitCode = await runCli([
  "plan",
  "sdk",
  "--json",
]);
```

Use the runtime API instead when the caller wants typed results rather than CLI exit-code and presentation behavior.
