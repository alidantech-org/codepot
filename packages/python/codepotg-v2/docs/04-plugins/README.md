# 04 — Installable plugin packages

CodepotG extensions are ordinary installable, versioned Python packages discovered through Python entry points. Official and third-party plugins use the same public contracts and receive no hidden access to core internals.

## Documents

- [`01-plugin-system.md`](01-plugin-system.md) — categories, descriptors, entry points, registries, contexts, trust, failures, and conformance.
- [`02-language-adapter-contract.md`](02-language-adapter-contract.md) — per-template target resolution, semantic services, typed rule families, imports/exports, capabilities, boundaries, and tests.
- [`03-template-engine-adapter-contract.md`](03-template-engine-adapter-contract.md) — immutable render context, engine rules, includes, sandbox, named outputs, cache, boundaries, and tests.
- [`04-source-pack-and-ecosystem-adapters.md`](04-source-pack-and-ecosystem-adapters.md) — source normalization, local/Git pack providers, project manifests, dependencies, package managers, and ecosystem actions.

## Initial packages

```text
codepotg-openapi
codepotg-language-typescript
codepotg-language-dart
codepotg-template-jinja
codepotg-pack-typescript-sdk
codepotg-pack-dart-sdk
codepotg-pack-flutter-sdk
```

Each package has its own design reference, detailed task ledger, test boundaries, and progress record.

## Locked rules

- Core never hardcodes official adapter behavior.
- Importing a package does not mutate a global registry.
- Discovery uses Python entry points and returns factories/descriptors.
- Runtime instances own registries and explicit least-authority contexts.
- Language adapters do not assume frameworks.
- Template engines do not own target syntax or outputs.
- Source adapters normalize directly to neutral IR.
- Ecosystem adapters plan manifest/toolchain intent but do not execute commands directly.
- Removing one optional plugin only removes its capabilities; core import continues to work.
