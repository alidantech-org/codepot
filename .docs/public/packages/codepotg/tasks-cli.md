---
title: Tasks and CLI reference
description: Run generation, initialize projects, inspect paths, build JSONL caches, and manage tasks.
product: codepotg
package: codepotg
order: 5
---

# Tasks and CLI reference

## Global commands

```bash
codepotg --version
codepotg --help
codepotg init
codepotg generate
codepotg jsonl
codepotg paths
codepotg task --help
```

## `generate`

```bash
codepotg generate [TASK_NAME] [OPTIONS]
```

Options:

| Option | Meaning |
|---|---|
| `-c, --config PATH` | Explicit `Codepotg.yaml` path |
| `--all` | Run every task in file order |
| `--dry-run` | Plan without writes or commands |
| `-v, --verbose` | Show files, command output, and more diagnostics |
| `-r, --refresh` | Clean configured paths before generation |
| `--skip-before` | Skip before commands |
| `--skip-after` | Skip after commands |
| `--debug` | Re-raise errors with a traceback |

Examples:

```bash
codepotg generate sdk
codepotg generate sdk --dry-run --verbose
codepotg generate --all
codepotg generate sdk --refresh
codepotg generate sdk --skip-after
```

When neither a task name nor `--all` is supplied, command behavior follows the runtime's task-selection rules and reports ambiguity when the configuration cannot select one task safely.

## Generation summary

The CLI reports task language, input, template root, output root, cleanup actions, managed writes, immutable creation/skips, refused writes, and diagnostics.

With `--verbose`, it also displays planned, written, updated, unchanged, and skipped files.

## `init`

```bash
codepotg init --yes
```

Creates a starter `Codepotg.yaml`. Without non-interactive flags, the command can prompt for project values.

## `paths`

```bash
codepotg paths ./templates/typescript
```

Validates and prints:

- resolved `paths.yaml` or default path configuration;
- import strategy;
- template extension and stripping behavior;
- raw-file support;
- default lifecycle;
- legacy folder recipes;
- selections;
- emissions, providers, and provided facts;
- barrels and exports.

Use this before running an unfamiliar pack.

## `jsonl`

The JSONL command compiles or refreshes a visible indexed source cache for an OpenAPI input. It is useful when diagnosing source indexing, cache reuse, or lazy lookup behavior.

The generated cache belongs under `.codepotg/cache` and is an implementation artifact, not a manually edited contract.

## `task`

The task command group manages task definitions in `Codepotg.yaml`. Use `codepotg task --help` to inspect the exact subcommands in the installed version.

Task editing preserves the distinction between CodepotG configuration and `CodepotFile.yml` used by `codepotx`.

## Exit behavior

Command errors print a user-facing message and exit with status 1. `--debug` additionally exposes the traceback for development diagnostics.

## Recommended scripts

```json
{
  "scripts": {
    "codegen:check": "codepotg generate sdk --dry-run --verbose",
    "codegen": "codepotg generate sdk",
    "codegen:refresh": "codepotg generate sdk --refresh"
  }
}
```

Do not use `--refresh` as the default until clean roots and generated ownership have been reviewed.