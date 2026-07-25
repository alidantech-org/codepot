---
title: Template packs and variables
description: Compile paths.yaml and Handlebars packs with strict variables, helpers, partials, selectors, requirements, and lifecycle metadata.
product: codepotx
package: codepotx
order: 5
---

# Template packs and variables

`codepotx` template packs use `paths.yaml` and Handlebars templates.

## Pack structure

```text
templates/typescript/
├── paths.yaml
├── models/
│   └── model.ts.hbs
├── services/
│   └── service.ts.hbs
├── partials/
│   └── header.hbs
└── static/
```

## Compilation

The templating engine discovers and validates:

- path configuration;
- templates and raw files;
- partials;
- helper references;
- selectors and aliases;
- variable requirements;
- output path tokens;
- managed and immutable lifecycle rules.

The result is `CompiledTemplatePack`.

## Variable catalog

`TemplateVariableCatalog` describes the stable variables a pack can use. Frontends can inspect the catalog without rendering templates.

Use variable inspection to:

- explain available context;
- validate required values;
- power editor completion;
- show a playground variable browser;
- detect pack/authoring incompatibility before generation.

## Strict rendering

Handlebars rendering uses strict missing-variable behavior with prototype access disabled.

This prevents a misspelled variable from silently rendering empty output and reduces unsafe object access.

## `paths.yaml`

A pack can declare:

- selections and aliases;
- templates and output paths;
- grouping;
- raw/static files;
- requirements and variables;
- lifecycle modes;
- dependency and import behavior;
- barrel or aggregate outputs.

Output path validation happens before project mutation.

## Helpers and partials

Helpers should be explicitly registered and represented in the compiled pack contract. Partials are discovered and validated before rendering.

A template must not rely on a helper or partial that is absent from the compiled pack.

## Source modes

Template packs can be resolved through supported source descriptors such as:

- local directories;
- packages;
- Git sources;
- artifacts;
- memory sources for tests or embedded tools.

Source resolution belongs to platform services, not the templating domain.

## Requirements

A pack can declare requirements for authoring features or context variables. Generation validates these requirements before rendering.

Examples include:

- entity metadata required;
- frontend metadata required;
- named variable required;
- target framework feature required.

## Context safety

Templates receive stable artifact-derived context. They do not receive mutable authoring builders, runtime services, filesystem handles, or CLI objects.

## Inspection

Use runtime or CLI variable operations:

```bash
codepotx variables sdk
codepotx inspect --json
```

## Design guidance

- Keep template packs project-owned when they encode project architecture.
- Treat paths and exported names as compatibility boundaries.
- Validate helpers, partials, and variables before rendering.
- Use strict missing-variable behavior.
- Keep platform access out of templates.
- Prefer stable artifact fields over compatibility shims.