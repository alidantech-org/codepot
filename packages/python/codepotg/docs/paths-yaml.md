# `paths.yaml` and `paths.yml` Graph Guide

CodepotG accepts either `paths.yaml` or `paths.yml` in one template pack. A pack must not contain both names.

The graph contract separates three concerns:

```text
selection  -> chooses source data
emission   -> renders one template from a selection
tbarrel    -> aggregates outputs from emissions or other barrels
```

`folders` remains supported as the legacy compatibility format. New packs should use named selections and emissions.

## Complete example

```yaml
imports:
  strategy: relative

write_policy:
  default_mode: managed
  managed_roots: [generated]
  immutable_roots: [generated/bootstrap]
  protected_roots: [src/manual]
  clean_roots: [generated]

selections:
  dtos:
    select: schemas.emit_dtos
    as: dto
    scope: each

  enums:
    select: schemas.emit_enums
    as: enum
    scope: each

  resource_operations:
    select: operations
    as: operations
    scope: resource

emissions:
  dto-types:
    selection: dtos
    template: templates/dto.type.ts.j2
    output: [generated, models, "[dto.name.path.o].ts"]
    provides: [dtos]

  dto-zod:
    selection: dtos
    template: templates/dto.zod.ts.j2
    output: [generated, schemas, "[dto.name.path.o].schema.ts"]
    provides: [dtos, validation]
    imports:
      enums: enum-types

  enum-types:
    selection: enums
    template: templates/enum.ts.j2
    output: [generated, models, "[enum.name.path.o].ts"]
    provides: [enums]

  operations:
    selection: resource_operations
    template: templates/resource.operations.ts.j2
    output: [generated, resources, "[selection.resource]", operations.ts]
    imports:
      dtos: dto-types
      enums: enum-types

barrels:
  models:
    template: templates/models.index.ts.j2
    output: [generated, models, index.ts]
    exports: [dto-types, enum-types]
    scope: all

  resource_models:
    template: templates/resource.index.ts.j2
    output: [generated, resources, "[barrel.resource]", index.ts]
    exports: [dto-types, enum-types]
    scope: resource
```

## Selections

A selection has a stable name independent of any template:

```yaml
selections:
  dtos:
    select: schemas.emit_dtos
    as: dto
    scope: each
```

Fields:

| Field | Required | Meaning |
|---|---:|---|
| `select` | yes | Documented source collection or canonical selection expression. |
| `as` / `alias` | no | Context variable used by templates and output expressions. Defaults to the selection name. |
| `scope` | no | `each`, `all`, or `resource`. Defaults to `each`. |
| `description` | no | Author-facing explanation displayed by `codepotg paths`. |

Selection aliases must be unique. `as` and `alias` are compatibility names for the same field and may not conflict.

### Selection scopes

`each`
: One output context per selected item. The alias is the selected item.

`all`
: One output context containing every selected item. The alias is an ordered tuple. `selection.count` reports its size.

`resource`
: One output context per resource. The alias is the ordered tuple belonging to that resource. `selection.resource` contains the resource identity.

The same selection can feed several emissions. CodepotG resolves the selection once, then each emission gets its own template, output path, providers, lifecycle, and result.

## Emissions

An emission is one named output producer:

```yaml
emissions:
  dto-types:
    selection: dtos
    template: templates/dto.type.ts.j2
    output: [generated, models, "[dto.name.path.o].ts"]
    provides: [dtos]
    imports:
      enums: enum-types
```

Fields:

| Field | Required | Meaning |
|---|---:|---|
| `selection` | yes | Name from `selections`. |
| `template` | yes | Safe relative template path. `..` and absolute paths are refused. |
| `output` | yes | Non-empty list of static and dynamic path parts. |
| `provides` | no | Semantic capabilities supplied by the output, such as `dtos`, `enums`, or `entities`. Defaults to the selection name. |
| `imports` | no | Mapping of dependency purpose to an explicit emission or barrel provider. |
| `lifecycle` | no | `managed` or `immutable`. Defaults to the write-policy mode. |
| `description` | no | Author-facing explanation. |

Output paths are normalized to relative POSIX paths before files exist. Collisions are rejected during planning.

## Explicit dependency providers

A dependent emission must identify its providers:

```yaml
emissions:
  operations:
    selection: operations
    template: operation.ts.j2
    output: [generated, operations, "[operation.name.path.o].ts"]
    imports:
      dtos: dto-types
      enums: enum-types
```

CodepotG resolves each required source ref against only these configured providers. Generation fails when:

- no configured provider emits the required ref;
- more than one configured provider emits the same required ref;
- the provider name does not exist;
- a provider output is ambiguous for the required resource scope.

Conflict validation uses actual effective refs, not only broad categories. A barrel containing enums and a direct DTO provider are valid together. A barrel and a direct provider that both contain the same required DTO are rejected.

## Barrels

A barrel is a first-class output node:

```yaml
barrels:
  models:
    template: models.index.ts.j2
    output: [generated, models, index.ts]
    exports: [dto-types, enum-types]
    scope: all
```

Fields:

| Field | Required | Meaning |
|---|---:|---|
| `template` | yes | Barrel template. |
| `output` | yes | Barrel output path. |
| `exports` | yes | One or more emission or barrel node names. |
| `scope` | no | `all` or `resource`. `each` is invalid for barrels. |
| `as` / `alias` | no | Barrel context variable. Defaults to `barrel`. |
| `lifecycle` | no | `managed` or `immutable`. |

A barrel template receives:

```text
barrel.name
barrel.scope
barrel.resource
barrel.members
barrel.symbols
barrel.provides
barrel.count
```

Each member is a virtual output with its source ref, output path, symbols, capabilities, resource, and status.

Barrels are not handled by a fixed “all barrels last” pass. The scheduler writes a barrel only after every member in its declared scope has been physically written or accepted as an existing immutable output. Nested barrels are scheduled through the same dependency graph.

## Bounded graph template context

Graph templates receive bounded globals:

```text
project
lang
emit
meta
selected_frontend
selected_frontends
frontend_count
file
output
providers
provider_outputs
selection
source
sources
resolve
resolver_stats
```

They also receive their declared selection alias, such as `dto`, `enum`, `operation`, or `resource`.

The complete `api`, `schemas`, `operations`, `resources`, `entities`, and `frontends` roots remain internal selection sources and are not copied into graph render contexts.

### `selection`

```text
selection.name
selection.select
selection.alias
selection.scope
selection.key
selection.item
selection.items
selection.resource
selection.count
```

### `source` and `sources`

`source` is a lazy indexed JSONL proxy when the output represents one source ref. `sources` is the ordered tuple for aggregate output.

Metadata such as `source.key`, `source.ref`, `source.kind`, and `source.resources` does not load the raw record. Mapping access triggers one indexed byte lookup:

```jinja
{{ source.kind }}
{{ source.get("description", "-") }}
{% for value in source.get("enum", ()) %}
  {{ value }}
{% endfor %}
```

### `resolve`

The bounded resolver supports:

```jinja
{% set user = resolve.ref("#/components/schemas/User") %}
{% set operation = resolve.operation("listUsers") %}
{% set resource_items = resolve.resource("users") %}
{% set users = resolve.mentions("tag", "users") %}
{% set dependants = resolve.dependants("#/components/schemas/User") %}
```

Returned objects remain lazy. Resolver caches enforce record-count, byte, related-item, and depth limits.

## Dynamic output parts

An output part may be static or dynamic:

```yaml
output:
  - generated
  - resources
  - "[selection.resource]"
  - "[operation.name.path.o].ts"
```

The existing path token rules remain available:

```text
[expression]   dynamic value
[[value]]      literal bracketed value
{{value}}      literal braced value
```

## Write lifecycle and safety

`managed`
: CodepotG creates and updates changed content.

`immutable`
: CodepotG creates the file once. Existing files are accepted as written dependencies without being modified.

All generated writes are atomic. A temporary sibling file is flushed and then replaced into place. Protected roots, out-of-root writes, invalid lifecycle roots, and output collisions are refused before rendering.

## Incremental scheduling

The graph runtime operates as:

```text
ready selection outputs
  -> bounded render workers
  -> byte-bounded file queue
  -> one atomic file writer
  -> written registry update
  -> release dependants
```

Progress states include selection resolution, planned, rendering, rendered, queued, written, unchanged, immutable skipped, failed, and completed.

## Legacy `folders` migration

Legacy packs continue to work:

```yaml
folders:
  dto:
    select: schemas.emit_dtos
    as: dto
    mode: each
    parts: [generated, models]
```

Migration steps:

1. Create a named selection from each distinct legacy `select` expression.
2. Create one named emission for each template/output behavior.
3. Move the template path and complete output path into the emission.
4. Add `provides` to provider outputs.
5. Add explicit `imports` to dependent emissions.
6. Replace aggregate index templates with barrels.
7. Run `codepotg paths <template-directory>` before generation.
8. Keep the legacy folder block temporarily when comparing output, then remove it after compatibility tests pass.

A pack may contain both legacy folders and the new graph while migrating. Explicit graph templates are planned only from graph declarations; legacy template scanning remains isolated to folder-only packs.

## Validation command

```bash
codepotg paths path/to/template-pack
```

The command reports:

- legacy folder recipes;
- named selections and scopes;
- emissions, output paths, capabilities, and provider edges;
- barrels, scopes, and export membership;
- unknown keys and invalid references;
- dependency cycles and unsafe template paths.
