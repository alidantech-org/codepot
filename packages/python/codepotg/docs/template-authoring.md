# Template Authoring Guide

This guide defines how CodepotG Jinja template packs consume the normalized contract. It describes template authoring only; implementation details belong outside template packs.

## Authoring flow

```text
paths.yaml selection
  -> contextual template variable
  -> normalized contract values
  -> language helpers and planned imports
  -> emitted file
```

Templates render facts. They do not parse OpenAPI, resolve `$ref`, merge entity inheritance, classify operation roles, or interpret arbitrary `x-codegen` dictionaries.

## Template-pack contents

A template pack can contain:

```text
paths.yaml
Jinja files ending in .j2
reusable Jinja partials
raw files copied without rendering
```

`paths.yaml` determines which collection a template iterates over, the name of its contextual variable, its output path, and whether the resulting files are managed or immutable.

## Global variables

Every template receives these stable roots:

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

`api` is the canonical language-neutral root. The shorter collection variables are convenience aliases.

## Contextual variables

Folder selections can add an active item:

```text
resource
schema
model
dto
enum
primitive
operation
field
parameter
request
request_body
response
entity
relation
constraint
frontend
screen
component
```

Prefer contextual collections. A resource template should normally use `resource.operations`, `resource.schemas`, and `resource.entities`; an operation template should use `operation.parameters`, `operation.request_body`, and `operation.responses`.

## Collections

Normalized collections expose:

```text
all
count
by_id
by_name
```

Specialized views provide clear classifications such as:

```text
operations.queries
operations.mutations
operations.lists
operations.details
operations.creates
operations.updates
operations.deletes
operations.actions
schemas.models
schemas.dtos
schemas.enums
schemas.primitives
schemas.requests
schemas.responses
entities.abstract
entities.persistent
resources.with_ui
resources.with_entities
```

Iteration order is deterministic. Lookup maps are provided for direct access without replacing ordered collections.

## Names

Named items expose casing and plurality variants:

```text
name.raw
name.clean
name.snake
name.kebab
name.camel
name.pascal
name.screaming
name.constant
name.dot
name.path
name.lower
name.upper
```

Each case exposes:

```text
o / original
s / singular
p / plural
number
```

Examples:

```jinja
{{ schema.name.pascal.o }}
{{ resource.name.kebab.o }}
{{ entity.name.snake.p }}
{{ operation.name.camel.o }}
```

Existing short aliases such as `sn`, `kb`, `cm`, `pc`, `ss`, `cn`, `dt`, and `pt` remain supported.

## Values and origin

Values that must distinguish missing, explicit `null`, inferred defaults, and inherited defaults expose:

```text
value
is_set
origin
is_authored
is_inferred
```

Origins are described as authored, inferred, derived, or effective. Template authors should use `is_set` whenever `null` is a valid authored value.

## References

References expose:

```text
ref
kind
name
owner
is_resolved
target
```

The original reference is retained even after a target is resolved. Templates use `target` rather than parsing JSON Pointer strings. Unresolved references remain visible and produce diagnostics.

## Schema use

One consistent schema-use shape is used for fields, parameters, media types, array items, composition branches, additional properties, frontend props, and entity schema links:

```text
ref
refs
schema
inline
kind
is_reference
is_inline
is_resolved
```

## Language helpers

`lang` contains target-language interpretation, including safe symbols, reserved-word handling, type names, literal formatting, imports, validation expressions, file naming, framework information, package information, and language feature flags.

Language-neutral meaning remains under `api` and contextual contract items.

## File context

After path planning, `file` exposes:

```text
output_path
relative_path
name
stem
suffix
depth
root_prefix
group
item_key
dependencies
imports
meta
```

Use `file.imports` and planned dependencies instead of reconstructing relative paths inside templates.

## paths.yaml

```yaml
folders:
  resources:
    select: resources.all
    as: resource
    mode: each
    parts:
      - generated
      - modules
      - [resource.name.path.o]

  global:
    mode: once
    parts:
      - generated
```

Selection modes:

```text
each   one rendering per selected item
group  one rendering for a selected group
once   one rendering without an item loop
```

Path syntax:

```text
{folder}       configured folder recipe
[expression]   dynamic path value
[[value]]      literal bracketed value
{{value}}      literal braced value
```

Example path:

```text
{resources}/[resource.name.kebab.o].controller.ts.j2
```

## Output ownership

Managed files may be regenerated. Immutable files are created once and preserved. Protected roots cannot be overwritten, and cleanup is limited to configured clean roots.

## Reusable partials

Use partials for repeated rendering patterns such as field declarations, validation chains, operation parameters, response unions, entity constraints, imports, and documentation sections. Partials may render normalized facts but must not repeat inference.

## Access order

Use data in this order:

1. normalized property;
2. derived convenience property;
3. preserved extension;
4. raw source as a final compatibility escape hatch.

## Authoring rules

- Use documented stable variables.
- Prefer contextual collections over global searches.
- Use resolved references while retaining source refs when the target format requires them.
- Use presence information for nullable defaults and constants.
- Keep language syntax in adapters and language packs.
- Use planned imports and paths.
- Do not depend on internal Python module names.
- Do not assume unknown extension values have a fixed shape.
