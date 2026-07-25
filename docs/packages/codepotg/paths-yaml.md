---
title: paths.yaml planning
description: Select normalized records, schedule emissions, declare providers, group outputs, and build barrels.
product: codepotg
package: codepotg
order: 7
---

# `paths.yaml` planning

`paths.yaml` is the declarative generation plan for a template pack.

It answers four questions:

1. Which normalized records are selected?
2. Which template renders each selection?
3. Where is each result written?
4. Which generated facts depend on other emissions?

## Complete graph example

```yaml
name: acme-project-sdk
version: 1.0.0

write_policy:
  default_mode: managed
  managed_roots:
    - generated
  clean_roots:
    - generated

selections:
  project_models:
    from: schemas.models
    where:
      resource: projects
    as: model

  project_operations:
    from: operations
    where:
      resource: projects
    as: operation

emissions:
  models:
    selection: project_models
    template: models/model.ts.j2
    path:
      - models
      - "{{ model.name | kebab }}.ts"

  services:
    selection: project_operations
    template: services/project-service.ts.j2
    mode: grouped
    group_by: resource.name
    path:
      - services
      - "{{ resource.name | kebab }}-service.ts"

barrels:
  root:
    path:
      - index.ts
    exports:
      - models
      - services
```

## Pack metadata

`name` and `version` identify the pack and help diagnostics, caching, and compatibility reporting.

## `write_policy`

Write policy can define:

- default lifecycle mode;
- managed roots;
- immutable roots;
- protected roots;
- clean roots.

See [Lifecycle safety](/docs/packages/codepotg/lifecycle-safety).

## `selections`

A selection names a stable subset of normalized data.

```yaml
selections:
  models:
    from: schemas.models
    where:
      resource: users
    as: model
```

Common concepts:

| Field | Meaning |
|---|---|
| `from` | Source collection or selector |
| `where` | Equality or supported filter conditions |
| `as` | Alias exposed to the template |
| `scope` | Selection scope where supported |

Selectors should use documented normalized collections such as `schemas.models`, `schemas.dtos`, `operations`, `resources`, `entities`, or frontends.

## `emissions`

An emission schedules a template against a selection.

```yaml
emissions:
  models:
    selection: models
    template: models/model.ts.j2
    path:
      - models
      - "{{ model.name | kebab }}.ts"
```

An emission can control:

- template path;
- output path parts;
- lifecycle mode;
- per-item or grouped mode;
- grouping key;
- explicit providers;
- provided facts;
- import and dependency behavior.

## Grouped emissions

```yaml
mode: grouped
group_by: resource.name
```

Grouped mode collects selected records by a stable key and renders one file per group. The group context includes the grouped items and the resolved group owner where available.

Use grouped mode for services, routers, registries, modules, or other files that aggregate multiple operations or models.

## Providers

Providers make cross-emission dependencies explicit.

A provider can supply facts such as:

- generated output paths;
- exported names;
- dependencies;
- imports;
- related resource or schema records.

Templates should consume declared providers instead of searching the complete source graph.

## Provided facts

An emission can declare facts that later emissions or barrels need. This creates a directed planning graph and allows cycle detection before rendering.

## Barrels

A barrel is scheduled after the emissions it exports.

```yaml
barrels:
  models:
    template: barrels/index.ts.j2
    path: [models, index.ts]
    exports: [models]
```

Barrels should consume planned member outputs, not scan the filesystem after writes.

## Legacy `folders`

Legacy packs can define folder recipes with selection, alias, mode, lifecycle, and path parts. They remain supported but do not provide the same explicit dependency graph.

## Validate a paths file

```bash
codepotg paths ./templates/typescript
```

The command displays resolved selections, emissions, providers, barrels, template behavior, and lifecycle defaults.

## Common errors

- unknown selection name;
- unknown source collection;
- duplicate output paths;
- provider cycle;
- barrel export references an unknown emission;
- template path escapes the pack root;
- output path escapes allowed roots;
- grouped emission lacks a valid grouping field.

Resolve planning errors before debugging Jinja content.