---
title: Template context model
description: Understand global values, normalized collections, bounded selections, aliases, providers, and file metadata.
product: codepotg
package: codepotg
order: 9
---

# Template context model

CodepotG exposes a stable normalized context rather than requiring templates to interpret OpenAPI dictionaries directly.

## Global context

The stable global surface includes:

```text
project
api
lang
emit
meta
resources
features
schemas
operations
entities
access
frontends
selected_frontend
selected_frontends
frontend_count
file
```

An emission additionally receives its declared selection alias, for example `model`, `operation`, or `resource`.

## `project`

```text
project.name
project.version
project.description
project.lang
project.emit
project.docs
project.meta
```

`project.name` is a complete naming object rather than a plain string. `project.lang` and `project.emit` provide selected adapter and output information.

## `api`

`api` is the canonical language-neutral contract:

```text
api.info
api.servers
api.security
api.security_schemes
api.resources
api.schemas
api.operations
api.entities
api.base_entities
api.access_policies
api.frontends
api.dependencies
api.extensions
api.raw
api.diagnostics
```

Use domain collections such as `schemas` and `operations` for convenient filtered views. Use `api` when root-level relationships or source information are required.

## Collection contracts

Major collection groups use a consistent shape:

```text
all
count
by_id
by_name
classified subsets
```

Examples:

```text
schemas.models
schemas.dtos
operations.queries
operations.mutations
entities.with_relations
resources.with_ui
frontends.by_name
```

## Selection aliases

A `paths.yaml` selection chooses a collection and exposes each item through an alias:

```yaml
selections:
  models:
    from: schemas.models
    as: model
```

The corresponding template receives `model` as the current selected item.

Grouped emissions may receive the item list plus a resolved owner such as `resource`.

## Providers

Provider outputs are explicit cross-emission facts. They can expose generated paths, imports, dependencies, exported names, or related records.

A template should not search unrelated global collections when the pack can declare the dependency as a provider.

## `emit`

```text
emit.output_path
emit.template_root
emit.dry_run
emit.contract_version
emit.current
```

Per-item emission facts include group, item key, ref, resource path, folder path, filename, dependency refs, resolved dependencies, and imports.

## `file`

```text
file.output_path
file.relative_path
file.name
file.stem
file.suffix
file.depth
file.root_prefix
file.group
file.item_key
file.dependencies
file.imports
file.meta
```

Use `file` for the currently planned output, not for arbitrary filesystem access.

## Documentation values

Major objects expose `docs`, commonly including summary, description, examples, and deprecation information.

Implementation guidance is available through ordered `info` categories.

## Language values

`lang` exposes the selected adapter, framework, package metadata, feature flags, and helper groups.

## Raw and extensions

Every normalized major object exposes:

```text
extensions
raw
```

Use them only after normalized values. Raw access is a compatibility escape hatch, not the primary template API.

## Context stability

New variables can be added while compatibility aliases remain available during pack migration. Pack authors should avoid depending on undocumented internal Python objects or object identity.