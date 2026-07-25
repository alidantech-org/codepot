---
title: Best practices and troubleshooting
description: Keep codepotx authoring, template packs, runtime integrations, and generation tasks deterministic, safe, and maintainable.
product: codepotx
---

# Best practices and troubleshooting

## Keep the public layers separate

Use the package entrypoint that owns the concept:

```ts
import { defineVersionContract, schema } from "codepotx";
import type { GenerationPlan } from "codepotx/contract";
import { createDefaultCodepotRuntime } from "codepotx/runtime";
```

Do not import private implementation folders. Published entrypoints are the compatibility boundary.

## Keep frontends thin

A CLI, editor, web interface, or MCP server should translate input into runtime operations and present typed results. It should not contain separate compiler, template, generation, or cleanup rules.

When behavior is needed by more than one frontend, add it to the runtime or the owning domain layer.

## Prefer complete plans

Inspect a plan and dry run before applying substantial changes:

```bash
codepotx validate
codepotx variables sdk
codepotx plan sdk --json
codepotx generate sdk --dry-run
```

Review output roots, lifecycle modes, stale cleanup, commands, unresolved variables, and refused writes.

## Keep template packs explicit

A pack should declare its selectors, variables, helpers, partials, requirements, output paths, and lifecycle behavior. Avoid templates that depend on undocumented global state or private artifact shapes.

Use strict missing-variable behavior. A missing value should produce a diagnostic rather than silently render an empty string into generated code.

## Keep output ownership narrow

Managed roots should contain only files the task is allowed to replace. Immutable files should be used for developer-owned scaffolds. Cleanup roots should be narrower than output roots when possible.

Never use broad project roots for stale cleanup.

## Keep commands optional and reviewable

Formatting and validation commands are reasonable task steps. Large shell scripts that perform hidden generation or deployment work are not.

Use `--skip-before`, `--skip-after`, or dry runs when diagnosing command failures.

## Treat artifacts as immutable values

Do not mutate compiled artifacts or plans after creation. If a transformation is required, create a new versioned artifact and preserve provenance.

This keeps caching, testing, serialization, and frontend inspection reliable.

## Use platform services for side effects

Domain modules should not call Node APIs directly. Files, commands, Git, clocks, IDs, caches, and source loading belong behind platform contracts.

This rule keeps memory adapters, tests, and future browser support viable.

## Troubleshooting

### Project configuration is not found

Run commands from the project root or pass explicit root, task-file, and authoring-config paths through the CLI. Confirm `CodepotFile.yml` and `codepotx.config.ts` are in the expected locations.

### Generation is refused

Check:

- `allow: true`;
- output and cleanup boundaries;
- managed versus immutable lifecycle;
- path traversal or collisions;
- existing developer-owned files;
- plan diagnostics.

A refusal is usually a safety result, not a filesystem failure.

### A template variable is missing

Run the variable inspection command and compare the pack's declared requirements with the compiled authoring artifact. Do not work around the problem with broad optional chaining in every template.

### Stale files remain

Verify that the files are present in the previous task manifest and inside an approved cleanup root. Files not proven to be task-owned should remain untouched.

### A command failed after rendering

Inspect the structured command result. Re-run with verbose output or skip commands to separate rendering issues from project-command issues.

### Runtime and CLI versions differ

The CLI is designed to prefer the consumer project's local `codepotx/runtime`. Install compatible project-local packages and avoid mixing unrelated workspace builds.

## Validation for contributors

```bash
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
pnpm --filter codepotx package:lint
```

Architecture, compatibility, contract, authoring, templating, generation, platform, runtime, and integration suites protect the package boundaries.
