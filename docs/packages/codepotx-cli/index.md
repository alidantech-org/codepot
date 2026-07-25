---
title: codepotx-cli
description: The official thin terminal frontend for the codepotx runtime, with project-local runtime resolution and machine-readable output.
product: codepotx-cli
---

# `codepotx-cli`

`codepotx-cli` exposes the `codepotx` terminal command. It owns argument parsing, project discovery, runtime loading, terminal presentation, and exit codes. The `codepotx` package owns authoring, template compilation, generation planning, filesystem safety, diagnostics, events, and execution.

The package is under active development with version `0.0.0`. It is documented here as the implemented workspace CLI, not as a stable published npm release.

## Why the CLI stays thin

```text
terminal arguments
      ↓
codepotx-cli
      ↓ typed runtime request
project-local codepotx/runtime
      ↓
typed result, diagnostics, and events
      ↓
terminal or JSON presentation
```

This boundary prevents terminal behavior from becoming a second engine. Web, editor, MCP, desktop, test, and embedded clients can call the same runtime operations.

## Main commands

```bash
codepotx validate
codepotx inspect --json
codepotx variables sdk
codepotx plan sdk --json
codepotx generate sdk --dry-run
codepotx generate sdk
codepotx features
codepotx help
codepotx version
```

## Learning path

1. [Getting started](/docs/packages/codepotx-cli/getting-started)
2. [Command reference](/docs/packages/codepotx-cli/commands)
3. [Global and command options](/docs/packages/codepotx-cli/options)
4. [Project-local runtime resolution](/docs/packages/codepotx-cli/runtime-resolution)
5. [JSON output and automation](/docs/packages/codepotx-cli/automation)
6. [Troubleshooting](/docs/packages/codepotx-cli/troubleshooting)

## Package boundaries

New compiler, authoring, templating, generation, platform, or safety behavior belongs in `codepotx`. The CLI may translate user input into runtime requests and render runtime responses; it must not duplicate domain logic.

## Development

```bash
pnpm --filter codepotx-cli typecheck
pnpm --filter codepotx-cli test
pnpm --filter codepotx-cli build
pnpm --filter codepotx-cli package:lint
```

The package is ESM-only and targets Node.js 22.18 or newer.
