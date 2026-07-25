---
title: codepotx-cli
description: The thin terminal frontend for the codepotx runtime and the codepotx command.
product: codepotx-cli
order: 13
---

# `codepotx-cli`

`codepotx-cli` is the official terminal frontend for [`codepotx`](/docs/codepotx).

It deliberately owns only command-line concerns:

- parsing arguments;
- locating the consumer project's runtime;
- subscribing to runtime events;
- presenting text or JSON output;
- translating results and errors into exit codes.

It does not own authoring, template compilation, generation planning, filesystem policy, or manifest behavior.

## Command

The package exposes:

```bash
codepotx
```

## Runtime resolution

The CLI prefers the consumer project's local `codepotx/runtime` installation. This keeps the engine version controlled by the project using it.

A compatible fallback dependency may be used when a project-local runtime is not available.

```text
terminal arguments
      ↓
codepotx-cli parser and presenter
      ↓
project-local codepotx/runtime
      ↓
typed runtime request and response
```

## Commands

```bash
codepotx validate
codepotx inspect --json
codepotx variables <task>
codepotx plan <task> --json
codepotx generate <task> --dry-run
codepotx generate <task>
codepotx features
codepotx version
codepotx help
```

## Options

```text
-r, --root <path>       Project root
-f, --file <path>       CodepotFile.yml path
-c, --config <path>     codepotx.config.ts path
-t, --task <name>       Task name
    --all               Run all configured tasks
    --dry-run           Plan and render without writes or commands
    --refresh           Refresh source and artifact caches
    --skip-before       Skip configured before commands
    --skip-after        Skip configured after commands
    --json              Machine-readable output
    --pretty            Pretty JSON output
-v, --verbose           Present runtime events
```

A positional value after task-oriented commands can also select the task:

```bash
codepotx plan sdk
codepotx generate sdk --dry-run
```

## Machine-readable use

Use `--json` when another tool is consuming results:

```bash
codepotx plan sdk --json
codepotx inspect --json
```

The CLI presenter should remain a view over structured runtime responses. New data needed by web, editor, or MCP frontends belongs in the runtime contract first.

## Exit behavior

- help and version output return success;
- successful runtime operations return zero;
- validation, generation, runtime loading, or presentation failures return a non-zero exit code;
- diagnostics remain part of the structured result and should be shown even when the process does not throw.

## Why it is a separate package

Separating the CLI proves that `codepotx` is a reusable engine rather than a terminal-bound application.

The same runtime can support:

- a graphical plan viewer;
- an editor command;
- a project dashboard;
- an MCP tool;
- an internal automation service.

Read [Build a runtime frontend](/docs/build-runtime-frontend) for the integration boundary.

## Status and publishing

The package is under active development with workspace version `0.0.0`. Its npm registry link remains TBD until the official release is published.

## Development

```bash
pnpm --filter codepotx-cli typecheck
pnpm --filter codepotx-cli test
pnpm --filter codepotx-cli build
pnpm --filter codepotx-cli package:lint
pnpm --filter codepotx-cli check
```

The package requires Node.js 22.18 or newer.
