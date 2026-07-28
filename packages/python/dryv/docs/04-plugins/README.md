# 04 — Installable adapter and infrastructure packages

Dryv adapters are ordinary installable, versioned Python packages discovered through Python entry points. Official and third-party packages use the same public contracts and receive no hidden access to core internals.

Plugins extend supported source formats, target validation/path capabilities, template engines, pack providers, ecosystems, writers, caches, and executors. They do **not** extend the semantic kernel.

## Documents

- [`01-plugin-system.md`](01-plugin-system.md) — categories, descriptors, entry points, registries, contexts, trust, failures, and conformance.
- [`02-language-adapter-contract.md`](02-language-adapter-contract.md) — per-template target detection, filename/identifier validation, path/module facts, strict non-rendering boundaries, and tests.
- [`03-template-engine-adapter-contract.md`](03-template-engine-adapter-contract.md) — immutable render context, engine rules, includes, sandbox, cache, boundaries, and tests.
- [`04-source-pack-and-ecosystem-adapters.md`](04-source-pack-and-ecosystem-adapters.md) — source normalization into the closed kernel, local/Git pack providers, project manifests, package managers, and ecosystem actions.

## Initial packages

```text
dryv-openapi
dryv-language-typescript
dryv-language-dart
dryv-template-jinja
dryv-pack-typescript-sdk
dryv-pack-dart-sdk
dryv-pack-flutter-sdk
```

Each package has its own design reference, detailed task ledger, test boundaries, and progress record.

## Locked rules

- Core owns and versions every semantic object, relation, facet, selector, and template-context property.
- Plugins cannot add semantic node kinds, facets, selectors, expression roots, or validators for invented concepts.
- Source adapters normalize only into the documented closed kernel.
- Language adapters detect/validate target files and calculate target-aware path/module facts; they do not render source syntax.
- Template engines render immutable prepared contexts and do not own target syntax, semantics, or outputs.
- Pack providers only resolve controlled snapshots.
- Ecosystem adapters plan known manifest/toolchain intent and do not expand the kernel.
- Importing a package does not mutate a process-global registry.
- Discovery uses Python entry points and returns factories/descriptors.
- Runtime instances own registries and explicit least-authority contexts.
- Removing one optional adapter removes only that input/target/engine/provider capability; core import continues to work.
