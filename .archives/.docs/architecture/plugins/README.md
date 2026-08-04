# 04 — Installable plugins

Dryv plugins are ordinary versioned Python packages discovered through standard entry points. Official and third-party packages use the same public contracts and receive no hidden access to runtime internals.

Plugins provide bounded capabilities such as target validation, module/path facts, template rendering, contract loading, pack resolution, ecosystem integration, writers, caches, and command execution. They do not extend the semantic kernel.

## Documents

- [`01-plugin-system.md`](01-plugin-system.md) — descriptors, entry points, runtime registries, trust, failures, validation, and conformance.
- [`02-language-adapter-contract.md`](02-language-adapter-contract.md) — target detection, identifier/path validation, module facts, and strict non-rendering boundaries.
- [`03-template-engine-adapter-contract.md`](03-template-engine-adapter-contract.md) — immutable contexts, sandboxing, partials, limits, diagnostics, and tests.
- [`04-source-pack-and-ecosystem-adapters.md`](04-source-pack-and-ecosystem-adapters.md) — canonical contract providers, pack providers, ecosystem adapters, and infrastructure boundaries.

## Current package family

```text
dryv
dryv-author
dryv-cli                    # planned standalone interface
dryv-language-typescript
dryv-language-dart
dryv-template-jinja
```

Reusable packs may be distributed independently without becoming Python runtime plugins.

## Locked rules

- Dryv owns and versions every semantic object, relation, facet, selector, and template-context property.
- Plugins cannot add semantic node kinds, facets, selectors, expression roots, or validators for invented concepts.
- Contract providers return only public immutable Dryv contracts.
- Language plugins validate target files and calculate path/module facts; they never render target syntax.
- Template engines render immutable prepared contexts and do not own semantics, planning, destinations, or writers.
- Pack providers resolve controlled immutable snapshots; they do not parse pack semantics outside the typed runtime loader.
- Ecosystem adapters plan known project-manifest or toolchain actions without expanding the semantic kernel.
- Importing a package does not mutate a process-global registry.
- Discovery uses Python entry points and returns validated factories.
- Runtime instances own plugin objects and least-authority contexts.
- Removing an optional plugin removes only that capability; importing and using the Dryv runtime still works.
