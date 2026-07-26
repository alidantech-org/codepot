# CodepotG v2 design documentation

These documents are the architecture baseline for the clean rewrite. The existing `packages/python/codepotg` package remains the old runtime; v2 does not implement old configuration decoders or import old internals.

## Mandatory reading

1. [`00-governance/00-approved-architecture.md`](00-governance/00-approved-architecture.md)
2. [`00-governance/01-agent-working-rules.md`](00-governance/01-agent-working-rules.md)
3. the design section for the assigned subsystem
4. [`tasks/PARALLEL_WORK.md`](tasks/PARALLEL_WORK.md)
5. the relevant core and package task ledgers

## Design sections

1. [`00-governance`](00-governance/00-approved-architecture.md) — locked decisions, parallel-agent rules, and change policy.
2. [`01-foundation`](01-foundation/README.md) — package structure, dependency direction, Python API, diagnostics, events, results, and cancellation.
3. [`02-configuration`](02-configuration/README.md) — complete `codepotg.yaml`, `CodepotgPack.yaml`, typed registry, rules, overrides, bindings, commands, toolchains, dependencies, and manifests.
4. [`03-generation`](03-generation/README.md) — pack file discovery, selections, folder patterns, static files, authored barrels, planning graphs, rendering, transactions, and cache.
5. [`04-plugins`](04-plugins/README.md) — plugin system and source, language, template-engine, pack-provider, and ecosystem adapter contracts.
6. [`05-distribution`](05-distribution/README.md) — Python-first interfaces, minimal and batteries-included packages, Git/GitHub packs, locks, and trust.
7. [`06-rewrite`](06-rewrite/01-clean-room-rewrite-policy.md) — clean-room policy and staged implementation plan without compatibility runtime.
8. [`tasks`](tasks/README.md) — task IDs, dependencies, acceptance criteria, parallel ownership, and progress evidence.

## Truth and change rule

Implementation must follow the approved documents. A design change requires the process in `00-governance/02-design-change-policy.md` and task updates before implementation.
