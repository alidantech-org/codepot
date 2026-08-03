---
title: JSON output and automation
description: Use codepotx-cli safely from scripts with machine-readable plans, diagnostics, results, stable exit codes, and project-local runtimes.
product: codepotx-cli
---

# JSON output and automation

`codepotx-cli` supports machine-readable output so scripts do not need to parse terminal formatting.

## Use JSON mode

```bash
codepotx validate --json
codepotx inspect --json
codepotx variables sdk --json
codepotx plan sdk --json
codepotx generate sdk --dry-run --json
```

Use `--pretty` for human-readable indentation:

```bash
codepotx plan sdk --json --pretty
```

Automation should rely on the structured runtime response and process exit code, not colored console text.

## Recommended validation flow

A safe automated workflow can run:

```bash
codepotx validate --json
codepotx plan sdk --json
codepotx generate sdk --dry-run --json
```

A later approved step can execute generation:

```bash
codepotx generate sdk --json
```

Inspect refusals, diagnostics, cleanup actions, and command results before treating the operation as successful.

## Stable information to consume

Depending on the operation, JSON results expose structured information such as:

- operation kind and status;
- diagnostics and severity;
- resolved task and source information;
- variable catalogs;
- planned files and lifecycle modes;
- created, updated, unchanged, immutable, skipped, refused, and deleted files;
- command outcomes;
- cancellation and failure details.

The runtime contract owns these values. The CLI serializes them without replacing them with presentation-only strings.

## Exit codes

Use the process exit code as the first automation gate, then inspect JSON for detail.

A non-zero code should cover invalid arguments, project-resolution failure, incompatible runtime, validation failure, or failed required execution. Warnings remain distinguishable from failures in the payload.

## Avoid global-version drift

Install or resolve the CLI together with a compatible project-local `codepotx` runtime. Automation should use the project lockfile and avoid silently substituting a different global engine.

## Do not hide destructive intent

Automation should keep these operations explicit:

- cache refresh;
- managed stale cleanup;
- before and after commands;
- non-dry-run generation.

A review stage should preserve the generated plan as an artifact or log when generation affects important project code.

## Programmatic CLI invocation

```ts
import { runCli } from "codepotx-cli";

const exitCode = await runCli([
  "validate",
  "--root",
  process.cwd(),
  "--json",
]);
```

Applications that need typed in-process results should call `codepotx/runtime` directly instead of capturing CLI output.
