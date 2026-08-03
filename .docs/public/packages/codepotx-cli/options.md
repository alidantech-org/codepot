---
title: Options reference
description: Understand project paths, task selection, dry runs, refresh, command skipping, JSON formatting, and verbose event output in codepotx-cli.
product: codepotx-cli
---

# Options reference

## Project location

```text
-r, --root <path>       Project root
-f, --file <path>       CodepotFile.yml path
-c, --config <path>     codepotx.config.ts path
```

Use `--root` when the current working directory is not the project root. Explicit file and config paths override normal project discovery.

Paths should identify project-owned files. The CLI passes resolved locations to the runtime instead of loading authoring or task configuration itself.

## Task selection

```text
-t, --task <name>       Task name
    --all               Run all tasks
```

Commands that require a task also accept a positional name:

```bash
codepotx plan sdk
codepotx generate sdk
```

Use `--all` only with commands that support multiple tasks. Task order follows the resolved project configuration.

## Safe execution controls

```text
    --dry-run           Render without writes or commands
    --refresh           Refresh source and artifact caches
    --skip-before       Skip before commands
    --skip-after        Skip after commands
```

`--dry-run` is the safest review mode. It should not mutate project files, delete stale files, or execute configured commands.

`--refresh` requests fresh source and artifact resolution. It is useful when caches may be stale, but it does not bypass validation or file-safety policy.

Skip controls help isolate rendering from project command failures.

## Output controls

```text
    --json              Machine-readable output
    --pretty            Pretty-print JSON output
-v, --verbose           Print runtime events
```

Use compact JSON for scripts and pretty JSON for human inspection. JSON mode should preserve typed diagnostics and result structure rather than embedding formatted terminal text.

Verbose mode presents runtime lifecycle events. Events are observational and do not replace the final operation result.

## Combining options

```bash
codepotx plan sdk \
  --root ./examples/acme \
  --json \
  --pretty

codepotx generate sdk \
  --dry-run \
  --refresh \
  --verbose
```

## Option ownership

The CLI owns option spelling and argument parsing. The runtime owns what project resolution, validation, planning, generation, cache refresh, and command execution mean.
