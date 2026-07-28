# Dryv design documentation

These documents are the architecture baseline for the clean rewrite. The existing `packages/python/dryv` package remains the old runtime; v2 does not implement old configuration decoders or import old internals.

## Mandatory reading

1. [`00-governance/00-approved-architecture.md`](00-governance/00-approved-architecture.md)
2. [`00-governance/04-closed-semantic-kernel.md`](00-governance/04-closed-semantic-kernel.md)
3. [`00-governance/01-agent-working-rules.md`](00-governance/01-agent-working-rules.md)
4. [`00-governance/03-glossary-and-ownership.md`](00-governance/03-glossary-and-ownership.md)
5. the design section for the assigned subsystem
6. [`tasks/PARALLEL_WORK.md`](tasks/PARALLEL_WORK.md)
7. the relevant core and package task ledgers

## Design sections

1. [`00-governance`](00-governance/00-approved-architecture.md) — locked decisions, closed semantic kernel, parallel-agent rules, change policy, terminology, and ownership.
2. [`01-foundation`](01-foundation/README.md) — package structure, dependency direction, Python API, diagnostics, events, results, and cancellation.
3. [`02-configuration`](02-configuration/README.md) — complete `dryv.yaml`, `DryvPack.yaml`, linked full example, typed registry, rules, overrides, bindings, commands, toolchains, dependencies, and manifests.
4. [`03-generation`](03-generation/README.md) — pack discovery, root-first fixed selectors, selection folders, static files, authored barrels, planning/impact graphs, rendering, transactions, and cache.
5. [`04-plugins`](04-plugins/README.md) — source, language, template-engine, pack-provider, and ecosystem adapter contracts within the closed-kernel boundary.
6. [`05-distribution`](05-distribution/README.md) — Python-first interfaces, minimal and batteries-included packages, Git/GitHub packs, locks, and trust.
7. [`06-rewrite`](06-rewrite/01-clean-room-rewrite-policy.md) — clean-room policy and staged implementation plan without compatibility runtime.
8. [`tasks`](tasks/README.md) — task IDs, dependencies, acceptance criteria, parallel ownership, and progress evidence.

## Truth and change rule

Implementation must follow the approved documents. A design change requires the process in `00-governance/02-design-change-policy.md` and task updates before implementation.

Historical progress entries and old-runtime documentation may contain superseded words such as `resource`, `model`, `entity`, `frontend`, `ui`, global-first selectors, or language-rendered imports. They are not v2 contracts.
