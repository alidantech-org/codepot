# codepotg-openapi

Installable OpenAPI source-adapter package for CodepotG v2.

This package will load and validate OpenAPI documents, resolve references, preserve source provenance, and normalize directly into the neutral CodepotG IR. It must not select templates, render code, apply target-language rules, write artifacts, run commands, or depend on CLI behavior.

## Planned entry point

```toml
[project.entry-points."codepotg.source_adapters"]
openapi = "codepotg_openapi.plugin:create_plugin"
```

## Boundaries

- Import only supported CodepotG public plugin, IR, diagnostic, and testing contracts.
- Keep OpenAPI-specific structures inside this package.
- Parse each document once per generation session.
- Produce deterministic immutable IR with source locations.
- Treat network reference loading as an explicit host-controlled capability.

See [`docs/tasks/00-package-plan.md`](docs/tasks/00-package-plan.md).
