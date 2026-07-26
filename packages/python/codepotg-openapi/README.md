# codepotg-openapi

Installable OpenAPI source-adapter package for CodepotG v2.

This package loads and validates OpenAPI documents, resolves references, decodes supported typed/versioned Codepot `x-codegen` metadata, preserves source provenance, and normalizes directly into the closed CodepotG semantic kernel.

It must not:

- select templates or packs;
- render target code or language syntax;
- write artifacts or run commands;
- depend on CLI behavior;
- expose OpenAPI parser/resolver objects to core or templates;
- add semantic objects, schema kinds, relations, facets, selectors, expression roots, or template-context values.

## Planned entry point

```toml
[project.entry-points."codepotg.source_adapters"]
openapi = "codepotg_openapi.plugin:create_plugin"
```

## Kernel mapping

The adapter maps standard OpenAPI and approved `x-codegen` metadata into known concepts:

```text
OpenAPI tags/grouping policy     → contract.groups
component schemas               → group.schemas
path operations                 → group.operations
parameters/request bodies       → operation.inputs
successful responses            → operation.outputs
error responses                 → operation.failures
HTTP path/method/bindings        → operation.facets.http
security schemes/requirements    → group.policies + access facets
x-codegen storage metadata       → group.storage.mappings
x-codegen interaction metadata   → group.views
x-codegen event metadata         → group.events + operation effects/facets
x-codegen listeners              → operations with trigger facets
x-codegen execution hooks        → operation execution facets
x-codegen workflows              → group.workflows
x-codegen compensation           → workflow step compensation
```

Unknown extensions may be preserved only through bounded immutable provenance/raw/extension values. They do not become new facets or selectors.

## Boundaries

- Import only supported CodepotG public source-adapter, kernel/IR, diagnostic, and testing contracts.
- Keep OpenAPI and `x-codegen` parsing structures inside this package.
- Parse each document once per generation session.
- Resolve each canonical reference once per session.
- Produce deterministic immutable kernel objects with source locations.
- Treat network reference loading as an explicit host-controlled capability.
- Validate `x-codegen` version/schema before semantic normalization.
- Report unsupported or ambiguous metadata rather than guessing framework behavior.

See [`docs/design/README.md`](docs/design/README.md) and [`docs/tasks/00-package-plan.md`](docs/tasks/00-package-plan.md).
