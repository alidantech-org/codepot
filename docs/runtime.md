---
title: Programmatic use
description: Run Codepot generation from a TypeScript application instead of the command line.
order: 14
---

# Programmatic use

The CLI is the easiest way to use Codepot in a project, but applications and developer tools can also run the same workflow from TypeScript.

```ts
import { createDefaultCodepotRuntime } from 'codepotx/runtime';

const runtime = createDefaultCodepotRuntime({
  projectRoot: process.cwd(),
});

const response = await runtime.execute({
  kind: 'generation.execute',
  input: {
    task: 'sdk',
    codepotFile: {
      projectRoot: process.cwd(),
    },
  },
});

if (!response.result.success) {
  console.error(response.result.diagnostics);
  process.exitCode = 1;
}
```

## Useful programmatic workflows

A TypeScript application can use Codepot to:

- validate an authored contract before a release;
- list the variables available to a template pack;
- create and display a generation plan;
- run a dry run and show proposed changes;
- generate files from a desktop app, editor extension, or internal developer portal;
- observe progress and diagnostics in a user interface.

## Use the same project files

Programmatic use still respects the three user-owned layers:

- `codepotx.config.ts` remains the contract source;
- the selected template pack still owns code style;
- `CodepotFile.yml` still owns the task, output directory, commands, and permissions.

This means a team can move between CLI, editor, and application integrations without maintaining different generation rules.

## Cancellation

Long-running generation can receive a cancellation signal. Codepot checks cancellation between major stages, and transactional tasks restore changed files when cancellation occurs after writing has begun.

## Diagnostics

Always read the returned diagnostics rather than relying only on thrown errors. Diagnostics explain invalid contracts, missing template variables, refused paths, preserved user files, command failures, and other decisions that users may need to act on.
