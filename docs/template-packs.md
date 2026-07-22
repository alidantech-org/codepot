---
title: Template packs
description: Package reusable output architecture with paths.yaml, Handlebars, partials, and static files.
order: 7
---

# Template packs

A template pack owns generated architecture. Codepot does not hardcode frameworks, folder structures, filenames, or import statements.

```text
templates/
├── paths.yaml
├── _partials/
│   └── generated-banner.hbs
├── {model}/
│   └── [model.name.snake].ts.hbs
└── .prettierrc
```

## Supported files

- Handlebars templates;
- reusable partials under `_partials/` or `partials/`;
- raw text or binary files;
- hidden files when `include_hidden: true`;
- ignored files through manifest patterns.

## Safe helpers

The default runtime exposes deterministic side-effect-free helpers such as `camel`, `pascal`, `snake`, `kebab`, `constant`, `title`, `json`, `join`, `indent`, and boolean helpers.

Unknown helper declarations fail during template-pack compilation. Prototype access is disabled during rendering.

## Validation

Codepot parses Handlebars ASTs without executing templates. Variables, helpers, partials, block parameters, `@data` references, selectors, requirements, and dynamic output paths are validated before rendering.
