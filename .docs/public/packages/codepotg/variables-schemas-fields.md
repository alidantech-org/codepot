---
title: Schema and field variables
description: Complete reference for schema collections, constraints, composition, arrays, objects, and fields.
product: codepotg
package: codepotg
order: 11
---

# Schema and field variables

## Schema collections

```text
schemas.all
schemas.count
schemas.by_id
schemas.by_name
schemas.models
schemas.dtos
schemas.enums
schemas.primitives
schemas.aliases
schemas.unknown
schemas.queries
schemas.params
schemas.bodies
schemas.requests
schemas.responses
schemas.shared
schemas.projected
schemas.composed
schemas.emit_models
schemas.emit_dtos
schemas.emit_enums
```

## Schema values

Each schema exposes:

```text
id
name
ref
kind
resource
role
shared
projection
dependencies
is_alias
alias_of
nullable
type
types
format
constraints
enum_type
enum_values
fields
composition
inherited_refs
has_field_overrides
array
object
query
docs
lang
emit
extensions
raw
```

### Identity and role

- `id` is the normalized registry identity.
- `name` is the full naming object.
- `ref` preserves the original reference where applicable.
- `kind` classifies model, DTO, enum, primitive, alias, composed, or unknown shapes.
- `role` records create, update, query, params, body, response, or another Codepot role.
- `resource` links the schema to its owning resource when known.

## Constraints

```text
default
const
examples
minimum
maximum
exclusive_minimum
exclusive_maximum
multiple_of
min_length
max_length
pattern
min_items
max_items
unique_items
min_properties
max_properties
read_only
write_only
deprecated
```

`default` and `const` are presence-aware, so explicit `null` remains different from an absent value.

## Composition

```text
composition.kind
composition.branches
composition.refs
composition.inline_branches
composition.is_all_of
composition.is_any_of
composition.is_one_of
composition.is_not
```

Each branch uses the normal schema-use shape and can be a ref or inline schema.

## Array information

```text
array.items
array.prefix_items
array.contains
array.min_items
array.max_items
array.unique_items
```

The source may also preserve advanced JSON Schema keywords under normalized constraints or `raw`.

## Object information

```text
object.additional_properties
object.pattern_properties
object.property_names
object.min_properties
object.max_properties
object.dependent_required
```

`additional_properties` distinguishes allowed, forbidden, typed, and referenced forms.

## Fields

Schema and entity fields share this core:

```text
id
name
required
nullable
type
schema
constraints
enum_values
description
query
docs
lang
emit
extensions
raw
```

Schema fields additionally expose:

- reference identity and resolved target;
- item schemas for arrays;
- inline and referenced composition;
- inherited/projected origin;
- target-language type helpers.

## Query capabilities

```text
field.query.enabled
field.query.exact
field.query.one_of
field.query.sortable
field.query.selectable
field.query.date
field.query.range
field.query.search
field.query.operators
```

Search values:

```text
enabled
prefix
contains
fuzzy
```

## Enum values

An enum schema exposes `enum_type` and ordered `enum_values`. Templates should preserve source values and use language helpers for identifiers or literals.

## Dependencies

`schema.dependencies` records referenced schemas and related generation facts. Prefer planned dependencies and file imports over recursively scanning field refs in the template.

## Example

```jinja
export interface {{ model.name.pascal }} {
{% for field in model.fields %}
  {{ field.name.camel }}{{ "?" if not field.required else "" }}: {{ field.lang.type }};
{% endfor %}
}
```

## Guidance

- Prefer `schema.kind` and `schema.role` over naming conventions.
- Use presence-aware values when rendering defaults.
- Preserve enum source values separately from target identifiers.
- Check nullable and required independently.
- Use normalized composition before `schema.raw`.