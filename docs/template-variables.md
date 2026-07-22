---
title: Template variables
description: List and validate the complete Handlebars context contract.
order: 8
---

# Template variables

Each compiled template pack can produce a versioned `TemplateVariableCatalog`. The catalog is JSON-safe and contains:

- flattened variable paths, kinds, scopes, nullability, and origins;
- per-folder aliases such as `model`, `dto`, `operation`, or `resource`;
- naming variants under `.name`;
- helper descriptors;
- partial descriptors;
- Handlebars data variables;
- template-pack requirements;
- diagnostics.

## List variables

```bash
codepotx variables sdk
codepotx variables sdk --json
```

Typical paths include:

```text
project.name.pascal
schemas.models[].name.snake
model.fields[]
model.emit.imports[].importPath
operation.lang.functionName
variables.packageName
file.outputPath
@root
@index
```

## Naming variants

Named objects expose:

```text
original
raw
camel
pascal
snake
kebab
constant
title
path
```

## Requirements

A pack can declare required or optional variables in `paths.yaml`:

```yaml
variables:
  required:
    - path: project.name.pascal
      kind: string
    - model.name.snake
  optional:
    - variables.packageName
```

Unknown required variables or incompatible kinds fail validation before rendering.
