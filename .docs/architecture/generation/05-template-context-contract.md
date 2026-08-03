# Prepared template-context contract

## Rule

Templates receive only documented immutable semantic, planning, option, binding, and dependency facts. They never receive contract providers, parsers, module loaders, filesystems, project roots, pack providers, writers, command executors, environments, secrets, authoring builders, or mutable registries.

Dryv resolves relationships before rendering so templates do not perform graph searches.

## Always-available roots

```text
project
pack
options
bindings
artifact
target
imports
exports
contract
```

### `project`

```text
project.name
```

### `pack`

```text
pack.id
pack.version
```

### `options`

Resolved immutable pack options, including defaults. Unknown project options fail before rendering.

### `bindings`

Explicit immutable project values supplied to the pack. Bindings do not become IR or hidden semantic relationships.

### `artifact`

```text
artifact.id
artifact.path
artifact.selection_key
artifact.semantic_id
artifact.template_id
```

Templates cannot change the destination.

### `target`

```text
target.id
```

Target-neutral rendered documents may have no target ID.

### `imports` and `exports`

```text
imports.<localName>.modules
exports.<selectionKey>.modules
```

Each module exposes planned facts such as:

```text
artifact_path
selection_key
semantic_id
specifier
symbols
```

Templates author the final statements and formatting.

## Selector-owned roots

A selected artifact receives only the roots active for its selector.

### Group and schema

```text
group
schema
```

### Operation

```text
operation
operation.inputs
operation.outputs
operation.failures
operation.effects
operation.facets
```

Referenced schemas are resolved where present.

### Storage mapping

```text
mapping
mapping.schema
mapping.fields
mapping.primary_key
mapping.indexes
```

Mapped field references resolve to public schema fields.

### View

```text
view
view.schema
view.parts
view.triggers
```

Triggers expose resolved operations and payload schemas.

### Workflow, policy, and event

```text
workflow
policy
event
```

### Value source

```text
value_source
value_source.operation
value_source.output
value_source.value_field
value_source.label_fields
value_source.search_input
```

### Presentation

```text
presentation
presentation.entries
```

### Presentation entry

```text
entry
entry.view
entry.address
entry.navigation_parent
entry.order
```

The outer `presentation` root remains active for an entry selector.

## Shared semantic metadata

Semantic records expose public kernel data:

```text
schema.data.documentation
schema.data.tags
schema.data.guidance
schema.data.provenance
```

The Jinja plugin may expose narrow immutable aliases such as `schema.tags`, `view.guidance`, or `presentation.provenance`. These aliases do not duplicate semantic data.

## Tags

Verified immutable tag records expose:

```text
values
empty
has(tag)
has_any(tag...)
has_all(tag...)
under(namespace)
```

Ordinary context records cannot call methods.

## Guidance

Guidance is an immutable tuple of categorized notes. It is explanatory and must not be interpreted as a hidden programming language.

## Names

Named records use the public name projections:

```text
x.name.raw.original
x.name.camel.original
x.name.pascal.original
x.name.snake.original
x.name.kebab.original
x.name.path.original
```

Path expressions and templates use the same semantic projections. Path expressions do not support calls, arbitrary indexing, or template filters.

## Strict inactive roots

A schema-selected template receives `schema`; a presentation-selected template does not. Accessing an inactive root is a strict undefined diagnostic. Packs use the correct fixed selector rather than probing arbitrary roots.

## Context limits

The engine validates and freezes every context before rendering. It enforces depth/item limits and rejects cycles, unsupported objects, unsafe mapping keys, arbitrary callables, private attributes, and mutable runtime values.

## Prohibited context roots

Packs and plugins cannot add roots such as:

```text
resource
entity
model
frontend
ui
runtime
filesystem
environment
secrets
writer
commands
provider
parser
pydantic
```

A recurring semantic need becomes a typed core contract and fixed selector. A project-specific generation hint normally begins as a namespaced tag, not a new context root.
