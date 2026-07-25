# codepotx-cli

`codepotx-cli` is the official terminal frontend for the `codepotx` runtime.

It deliberately owns only argument parsing, project-runtime discovery, terminal presentation, and process exit codes. Authoring, template compilation, generation planning, filesystem safety, diagnostics, events, and execution remain in `codepotx`.

This boundary allows the same runtime operations to be reused by future web interfaces, editor extensions, MCP servers, desktop tools, AI integrations, and embedded Node.js applications without copying CLI behavior.

## Status

The package is under active development alongside `codepotx`. Its package version is currently `0.0.0`, so it should not yet be documented as a published stable npm release.

## Binary

```text
codepotx
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
codepotx help
codepotx version
```

## Options

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
    --pretty            Pretty-print JSON output
-v, --verbose           Print runtime events
```

A positional task name is accepted where a command requires one.

## Runtime resolution

For normal commands the CLI loads the consumer project runtime, subscribes to runtime events for presentation, executes the requested operation, then disposes the subscription.

The CLI prefers the project-local `codepotx/runtime` installation. This keeps the frontend aligned with the runtime version selected by the project instead of embedding a second copy of domain behavior.

## Programmatic entrypoint

```ts
import { runCli } from 'codepotx-cli';

const exitCode = await runCli([
  'plan',
  'sdk',
  '--json',
]);
```

## Development

```bash
pnpm --filter codepotx-cli typecheck
pnpm --filter codepotx-cli test
pnpm --filter codepotx-cli build
pnpm --filter codepotx-cli package:lint
```

The package is ESM-only and targets Node.js 22.18 or newer.

## Architectural rule

New compiler, authoring, templating, generation, platform, or safety behavior must be implemented in `codepotx`, not in this package. The CLI may translate user input into runtime requests and render runtime responses; it must not become a second engine.

## License

MIT
