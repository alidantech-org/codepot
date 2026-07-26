# CodepotG v2 design documentation

The documents are intentionally grouped in implementation order.

1. [`01-foundation`](01-foundation/README.md) — polished package structure, dependency direction, public API, and testing rules.
2. [`02-configuration`](02-configuration/README.md) — typed project and pack contracts, templates, bindings, overrides, commands, and setup.
3. [`03-generation`](03-generation/README.md) — planning, selection, static files, imports, barrels, execution, and transactions.
4. [`04-plugins`](04-plugins/README.md) — installable source, language, template-engine, and pack packages.
5. [`05-distribution`](05-distribution/README.md) — bundled defaults, Git-hosted packs, Python API, CLI, server, and MCP usage.
6. [`06-migration`](06-migration/README.md) — compatibility with the existing `codepotg.yaml`, `paths.yaml`, packs, and outputs.
7. [`tasks`](tasks/README.md) — executable rewrite backlog and progress records.

These documents are the architecture baseline. Changes must update the relevant document and task record before or with implementation.
