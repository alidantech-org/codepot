# OpenAPI source adapter design reference

## Role

This package loads OpenAPI YAML/JSON, validates and resolves references once, and normalizes directly into the neutral CodepotG IR.

It does not select target languages, templates, packs, outputs, commands, or files.

## Planned plugin entry point

```toml
[project.entry-points."codepotg.source_adapters"]
openapi = "codepotg_openapi.plugin:create_plugin"
```

## Project configuration example

```yaml
sources:
  backendApi:
    adapter: openapi
    path: ./openapi.yaml
    options:
      validation: strict
      externalReferences: localOnly
      maxReferenceDepth: 64
```

All options are typed and target-neutral.

## Processing

```text
controlled source loader
        ↓
safe YAML/JSON parse with spans
        ↓
OpenAPI structural validation
        ↓
canonical reference resolution
        ↓
direct neutral IR normalization
        ↓
immutable source result + digest
```

No compatibility graph or duplicate target-specific model is produced.

## Boundaries

The adapter may preserve approved OpenAPI provenance/extensions in bounded immutable IR extension values. It may not expose parser nodes, raw mutable mappings, reference resolver instances, or OpenAPI library classes to core consumers.

External references require host-authorized loaders and cannot obtain arbitrary filesystem/network access from project config alone.

See `../tasks/00-package-plan.md` and the core source-adapter contract.
