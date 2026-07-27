# Prepared template-context contract

## Rule

Templates receive only documented immutable semantic, planning, option, binding, and dependency values. They never receive the source adapter, parser, resolver, filesystem, project root, pack provider, writer, command executor, environment, secrets, or mutable registries.

The orchestrator prepares relationships before rendering so templates do not perform graph searches.

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

Resolved pack option values, including defaults:

```jinja
{% if options.mode == "strict" %}
{% endif %}
```

Unknown project options fail before rendering.

### `bindings`

Immutable project binding values supplied to the pack. Binding values remain explicit project data; they do not become IR or semantic relationships.

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

A target-neutral rendered document may have `target.id == none`.

### `imports` and `exports`

```text
imports.<localName>.modules
exports.<selectionKey>.modules
```

Each module exposes:

```text
artifact_path
selection_key
semantic_id
specifier
symbols
```

Example:

```jinja
{% for module in imports.types.modules %}
import type { {{ module.symbols | join(", ") }} } from "{{ module.specifier }}";
{% endfor %}
```

The text remains template-owned.

## Selector-owned roots

A selected artifact receives its active outer and inner roots.

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

Each input/output/failure resolves its referenced schema where present.

### Storage mapping

```text
mapping
mapping.schema
mapping.fields
mapping.primary_key
mapping.indexes
```

Mapped field references are resolved to schema fields.

### View

```text
view
view.schema
view.parts
view.triggers
```

Triggers expose referenced operations and payload schemas.

### Workflow, policy, and event

```text
workflow
policy
event
```

Events expose resolved payload/context schemas.

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

The outer `presentation` root is also active for an entry selection.

## Shared semantic metadata

Semantic records expose `KernelData` through their normal `data` field:

```text
schema.data.documentation
schema.data.tags
schema.data.guidance
schema.data.provenance
```

The Jinja adapter also provides narrow read-only aliases:

```text
schema.documentation
schema.tags
schema.guidance
schema.provenance

operation.tags
view.tags
presentation.tags
```

These aliases do not duplicate data in IR.

## Tags

```text
tags.values
tags.empty
tags.has(tag)
tags.has_any(tag...)
tags.has_all(tag...)
tags.under(namespace)
```

Examples:

```jinja
{% if view.tags.has("ui:data-table") %}
{% endif %}

{% if schema.tags.has_any("orm:custom", "repository:manual") %}
{% endif %}
```

Only the dedicated immutable tag record exposes these callables. Ordinary context records cannot call methods.

## Guidance

Guidance is an immutable tuple of categorized notes:

```jinja
{% for note in view.guidance %}
{{ note.kind.value }}: {{ note.text }}
{% endfor %}
```

Guidance is explanatory. Templates must not treat prose as a hidden programming language.

## Names

Named semantic records use:

```text
x.name.raw.original
x.name.camel.original
x.name.pascal.original
x.name.snake.original
x.name.kebab.original
x.name.path.original
```

Number projections remain in the documented `name.<case>.<number>` order.

Path expressions and Jinja use the same semantic naming projections, but path expressions do not support calls, arbitrary indexing, or template filters.

## Absent roots are strict undefined

A template selected for a schema receives `schema`; a presentation template does not automatically receive `schema`.

Accessing an inactive root is a strict undefined diagnostic. Packs must use the correct selector rather than probe arbitrary roots.

## Context size and depth

The Jinja adapter validates and freezes every context before rendering. It enforces configured depth/item limits and rejects cycles, unsupported objects, arbitrary mappings with unsafe keys, callables, private attributes, and mutable runtime values.

## Prohibited context additions

Packs and adapters cannot add roots such as:

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
source
openapi
pydantic
```

A recurring semantic need becomes a typed core contract and fixed selector. A project-specific generation hint normally begins as a namespaced tag, not a new context root.
