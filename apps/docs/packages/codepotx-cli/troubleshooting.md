---
title: Troubleshooting codepotx-cli
description: Diagnose project discovery, runtime compatibility, task selection, JSON output, refused writes, commands, and CLI development issues.
product: codepotx-cli
---

# Troubleshooting `codepotx-cli`

## Command not found

The package is still under active workspace development and is not documented as a stable published release. Build or run it through the repository workflow, and confirm the generated binary or package link is available on the current `PATH`.

```bash
pnpm --filter codepotx-cli build
```

## Project configuration cannot be found

Run from the project root or provide explicit paths:

```bash
codepotx validate \
  --root ./my-project \
  --file ./my-project/CodepotFile.yml \
  --config ./my-project/codepotx.config.ts
```

Confirm exact filename casing and that the files are readable.

## Project-local runtime cannot be loaded

Confirm the project has a compatible local `codepotx` package and that the supported `codepotx/runtime` entrypoint exists. Do not point the CLI at private source folders.

Reinstall from the project lockfile when dependencies are incomplete.

## CLI and runtime are incompatible

The CLI frontend and runtime operation contracts must be compatible. Use package versions developed or released together, and avoid combining an old global CLI with an unrelated project runtime.

A compatibility failure should be explicit rather than silently falling back to another engine.

## A task is not selected

Pass the task positionally or with `--task`:

```bash
codepotx plan sdk
codepotx plan --task sdk
```

Use `--all` only with commands that support every configured task.

## Generation is refused

The CLI is presenting a runtime safety result. Inspect the plan and diagnostics for:

- missing `allow: true`;
- output outside approved roots;
- managed or immutable ownership conflict;
- unsafe stale cleanup;
- duplicate output paths;
- unresolved variables or templates;
- path traversal.

```bash
codepotx plan sdk --json --pretty
codepotx generate sdk --dry-run --verbose
```

## Before or after command fails

Separate rendering from project commands:

```bash
codepotx generate sdk --dry-run
codepotx generate sdk --skip-before
codepotx generate sdk --skip-after
```

Use verbose output to inspect runtime command events. Keep command logic narrow and project-owned.

## JSON output is mixed with presentation text

Use `--json` without terminal-only processing. Automation should consume stdout according to the command contract and treat stderr as diagnostics or fatal presentation when applicable.

The CLI implementation should never inject decorative terminal output into a machine-readable JSON payload.

## Keyboard interruption or cancellation

A cancellation should propagate through runtime cancellation services and return a structured cancelled result. If work continues after interruption, inspect the platform adapter or command process cancellation path rather than adding frontend-only state.

## Contributor checks

```bash
pnpm --filter codepotx-cli typecheck
pnpm --filter codepotx-cli test
pnpm --filter codepotx-cli build
pnpm --filter codepotx-cli package:lint
```

New domain behavior belongs in `codepotx`; CLI fixes should remain limited to parsing, discovery, presentation, and exit-code translation.
