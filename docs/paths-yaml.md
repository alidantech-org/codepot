---
title: paths.yaml
description: Define selections, aliases, output paths, file lifecycles, partials, and variable requirements.
order: 9
---

# `paths.yaml`

```yaml
name: typescript-sdk
version: 1.0.0
template_extension: .hbs
strip_template_extension: true
allow_raw_files: true
include_hidden: true
ignore:
  - '*.tmp'

folders:
  model:
    select: schemas.models
    as: model
    mode: each
    parts:
      - src
      - models
      - [model.name.snake]

write:
  default_mode: managed
  clean_roots: [src]
  protected_roots: [src/manual]
```

## Folder modes

- `once` emits one file for the root context.
- `each` emits one file for every selected item and exposes it under the alias.
- `group` emits one file for the selected collection and exposes both the alias and `items`.

## Path tokens

- `{model}` identifies a configured template group.
- `[model.name.snake]` resolves a dynamic output segment.
- normal text remains static.

Dynamic path expressions are validated against the same variable catalog used for templates.

## Lifecycles

- `managed` files can be updated and become manifest-owned.
- `immutable` files are created once and then preserved.

Clean roots are scopes for stale managed files, not instructions for broad recursive deletion.
