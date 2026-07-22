---
title: CLI
description: Use the external codepotx frontend for validation, inspection, planning, variable discovery, and generation.
order: 12
---

# CLI

The CLI is published separately as `codepotx-cli` and exposes the `codepotx` binary. It imports only public `codepotx` subpaths and delegates all domain work to the runtime.

```text
codepotx validate
codepotx inspect --json
codepotx variables <task>
codepotx plan <task> --json
codepotx generate <task> --dry-run
codepotx generate <task>
codepotx features
```

## Common options

```text
-r, --root <path>       Project root
-f, --file <path>       CodepotFile.yml path
-c, --config <path>     codepotx.config.ts path
-t, --task <name>       Task name
    --all               Run all tasks
    --dry-run           Render without writes or commands
    --refresh           Refresh source and artifact caches
    --skip-before       Skip before commands
    --skip-after        Skip after commands
    --json              Machine-readable output
    --pretty            Pretty JSON
-v, --verbose           Print runtime events
```

The CLI prefers the consumer project's local `codepotx/runtime` installation and falls back to its compatible dependency.
