# Tags and template context

## Purpose

Tags provide a simple escape hatch while Codepot design is still evolving. They let authors and templates coordinate project-specific generation choices without requiring a new typed facet for every experiment.

## Model

Tags are immutable, sorted, unique, namespaced Boolean identifiers:

```text
orm:prisma
orm:prisma:custom_sql
ui:data-table
ui:filter:advanced
repository:custom
defytickets:organiser
```

Recommended grammar:

```text
segment(:segment)*
segment = [a-z][a-z0-9_-]*
```

Uppercase and malformed tags are rejected rather than silently normalized.

## Availability

Tags should be available on meaningful semantic objects through shared kernel data, including contracts, groups, schemas, fields, operations, storage mappings, events, policies, views/parts, workflows/steps, and presentations when those objects exist.

## Safe template API

```text
tags.values
tags.empty
tags.has(tag)
tags.has_any(*tags)
tags.has_all(*tags)
tags.under(namespace)
```

The value is immutable. No callbacks, mutation, regex execution, or arbitrary lookup are exposed.

## Rules

- Tags guide choices; they do not redefine object kinds.
- Tags do not replace refs or relationships.
- Tags do not duplicate typed facts such as requiredness, nullability, HTTP method, or schema type.
- Tags do not inherit automatically.
- Unknown tags are preserved and normally ignored.
- `codepot:*` is reserved for core.
- Pack and project namespaces are allowed.
- Tags begin as Boolean hints, not key/value configuration or a hidden programming language.
- Canonical IR transport and digest include tags.

## Promotion path

A widely used tag with stable semantics may later become a typed kernel property through the normal architecture-change process. Existing tags can be migrated explicitly.

## Core gate

Because templates and shipped IR must see tags consistently, tags require a typed core `TagSet` and template-context support. The author package must not keep tags only in Python builder state or encode them as arbitrary extensions.
