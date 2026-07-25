---
title: Entity, relation, access, and runtime variables
description: Complete reference for persistence fields, relations, constraints, policies, cache effects, hooks, and transport metadata.
product: codepotg
package: codepotg
order: 13
---

# Entity, relation, access, and runtime variables

## Entity collections

```text
entities.all
entities.count
entities.by_id
entities.by_name
entities.abstract
entities.persistent
entities.with_relations
entities.with_constraints
entities.with_backend_fields
entities.queryable
```

## Entity values

```text
id
name
kind
abstract
resource
schema
store
visibility
extends
declared_fields
inherited_fields
fields
backend_fields
storage_fields
public_fields
editable_fields
readonly_fields
queryable_fields
relations
constraints
info
docs
emit
extensions
raw
```

## Entity fields

```text
id
name
schema
type
required
nullable
role
generated
unique
indexed
immutable
readonly
editable
managed
selectable
backend_only
query
constraints
info
declared_on
inherited
explicit
extensions
raw
```

`explicit` records whether behavior was authored or supplied by normalization defaults.

## Relations

```text
id
name
cardinality
target
local_fields
foreign_fields
on_delete
on_update
nullable
owning
inverse
is_to_one
is_to_many
extensions
raw
```

Use resolved `target` for imports and generation. Preserve the original relation reference where diagnostics or compatibility require it.

## Constraints

```text
id
name
kind
fields
unique
rule
extensions
raw
```

Rule expressions preserve:

- operation;
- field;
- value;
- arguments;
- condition;
- result branches;
- original operation name;
- raw arguments.

## Access collections

```text
access.all
access.count
access.by_id
access.by_name
access.global
access.resource_scoped
```

Each policy exposes:

```text
id
name
owner
context
roles
permissions
tags
public
authenticated
info
extensions
raw
```

An operation access use exposes:

```text
ref
policy
is_resolved
```

## Runtime values

```text
operation.runtime.transport
operation.runtime.hooks
```

### Transport

```text
inbound.ip
inbound.user_agent
inbound.headers
inbound.cookies
outbound.cookies
outbound.headers
```

### Hooks

```text
before_handler
after_success
after_error
```

Each hook use exposes the original ref, resolved hook, lifecycle phase, and stable order.

## Cache effects

Cache read and invalidation values are documented with operation variables, but entity or access templates may consume resolved resource targets and tags through providers.

## UI and behavior flags

Resources and operations share:

```text
ui.enabled
ui.infer
ui.inferred
ui.role
ui.effective_enabled
ui.inference_source
ui.inference_reason
```

Authored and inferred states remain distinguishable.

## Example entity template

```jinja
export class {{ entity.name.pascal }} {
{% for field in entity.storage_fields %}
  {{ field.name.camel }}: {{ field.lang.type }};
{% endfor %}
}
```

A real persistence pack should also consume relation, constraint, generated strategy, and lifecycle metadata.

## Guidance

- Use normalized behavior flags instead of deriving them from field names.
- Keep public and backend fields separate.
- Resolve relation targets before rendering imports.
- Preserve delete/update behavior explicitly.
- Generate access implementations from policy meaning, not raw framework annotations.
- Treat unresolved refs as diagnostics, not empty values.