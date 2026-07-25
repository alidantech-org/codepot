---
title: Getting started with codepotx-cli
description: Run the workspace CLI against a project-local codepotx runtime and inspect, plan, dry-run, and generate a task safely.
product: codepotx-cli
---

# Getting started with `codepotx-cli`

The CLI currently ships from the Codepot workspace while the package is prepared for release. It expects a compatible project-local `codepotx` runtime and a project configured with `codepotx.config.ts` and `CodepotFile.yml`.

## Build the workspace packages

From the repository root:

```bash
corepack enable
pnpm install
pnpm --filter codepotx build
pnpm --filter codepotx-cli build
```

For development, run the workspace command through the package scripts or link the CLI into a test project according to the repository workflow.

## Prepare a project

A typical project contains:

```text
my-project/
├── codepotx.config.ts
├── CodepotFile.yml
├── templates/
│   └── sdk/
└── src/
```

The task file must explicitly allow generation:

```yaml
allow: true

tasks:
  sdk:
    authoring: ./codepotx.config.ts
    templates: ./templates/sdk
    output: ./generated/sdk
```

## Validate before generation

```bash
codepotx validate
```

Validation loads the project configuration through the runtime and reports authoring, template, task, source, and compatibility diagnostics.

## Inspect the project

```bash
codepotx inspect
codepotx inspect --json --pretty
```

Use inspection to understand the resolved project and runtime inputs without applying generation.

## Inspect template variables

```bash
codepotx variables sdk
```

This command asks the runtime for the task's template-variable catalog. It is useful before writing templates or diagnosing missing values.

## Plan and dry run

```bash
codepotx plan sdk --json --pretty
codepotx generate sdk --dry-run
```

The plan exposes intended outputs, lifecycle modes, dependencies, commands, cleanup, refusals, and diagnostics. A dry run renders without writes or commands.

## Generate

```bash
codepotx generate sdk
```

Review the resulting created, updated, unchanged, immutable, skipped, refused, and cleaned files. Treat warnings and refusals as structured outcomes rather than relying only on process text.

## Use explicit project paths

When running outside the project root:

```bash
codepotx validate \
  --root ./examples/acme \
  --file ./examples/acme/CodepotFile.yml \
  --config ./examples/acme/codepotx.config.ts
```

## Next steps

- [Commands](/docs/packages/codepotx-cli/commands)
- [Options](/docs/packages/codepotx-cli/options)
- [Runtime resolution](/docs/packages/codepotx-cli/runtime-resolution)
