# Authoring-aligned closed IR additions

## Status

This document is the authoritative alignment for the authoring discoveries implemented on `chatgpt/codepotx-restart-orchestrator`. It extends the closed kernel without creating a second author graph, generic fact bag, target binding system, database DSL, REST DSL, or UI framework model.

The following concepts are core-owned, typed, immutable, source-neutral, and transported through the canonical IR format:

- namespaced tags and categorized guidance;
- field lifecycle/query/reference capabilities;
- operation-backed value sources;
- contract-level presentations and view placements.

Any older document that describes these as author-only proposals is superseded by this document after the orchestrator branch passes verification and merges.

## One compilation target

Every authoring frontend produces the same `codepotg.ir.Contract`:

```text
Python codepotg-author ───────────┐
OpenAPI adapter ──────────────────┤
Canonical IR JSON/YAML ───────────┼──> Contract
Future native Codepot language ───┘
```

Pydantic models, decorators, builder objects, Python functions, ref registries, source-parser objects, and authoring projections never enter IR or render contexts.

## Tags

`KernelData.tags` is an immutable sorted `TagSet`.

Tag grammar:

```text
segment(:segment)*
segment = [a-z][a-z0-9_-]*
```

Examples:

```text
orm:prisma
orm:prisma:custom_sql
ui:data-table
repository:manual
defytickets:organiser
```

Tags are Boolean namespaced hints. They may influence pack/template choices but do not:

- create semantic relationships;
- replace typed fields/facets;
- add selectors;
- register context roots;
- carry arbitrary values;
- contain source code.

Safe template API:

```jinja
{% if view.tags.has("ui:data-table") %}
{% endif %}

{% if schema.tags.has_any("storage:custom", "repository:manual") %}
{% endif %}

{% if operation.tags.has_all("api:public", "testing:fixture") %}
{% endif %}

{% for tag in presentation.tags.under("navigation") %}
{% endfor %}
```

Known semantics still use typed properties. A field must not use `required`, `nullable`, or `references:Company:id` tags when typed contracts already exist.

Tags do not inherit automatically. Templates may inspect outer context tags explicitly.

## Categorized guidance

`KernelData.guidance` contains unique `GuidanceNote` values with a closed `GuidanceKind`:

```text
explain
implement
security
persistence
transaction
caching
testing
observability
ux
accessibility
ai
```

Guidance explains intent to templates, documentation packs, audits, and AI agents. It does not create hidden semantic behavior.

Example authoring intent:

```python
view.info(
    lambda info: (
        info.explain("Main admin page for browsing apps.")
        .implement("Render filters above the table and keep pagination in URL state.")
        .testing("Verify filters survive page reload.")
    )
)
```

A caching guidance note does not create a cache policy. Typed semantic declarations remain required for behavior.

## Field capabilities

A schema remains structural. `SchemaField.capabilities` contains broad reusable intent:

```text
FieldCapabilities
├── lifecycle
│   ├── initialize: caller | system | derived | forbidden
│   ├── mutate: caller | system | derived | forbidden
│   └── visibility: exposed | internal | sensitive
├── query
│   ├── operators
│   ├── sortable
│   └── selectable
└── reference
    ├── target_schema
    └── target_field
```

These facts are neutral:

- they do not generate an operation automatically;
- they do not define SQL, Mongo, HTTP, repository, or UI syntax;
- they do not override operation access/policy;
- they do not make a schema an entity.

Authoring may derive ordinary structural schemas from these capabilities. The author compiler must make derivation explicit, deterministic, inspectable, and eventually sealable. The resulting IR contains normal schemas, never `model`, `entity`, `request`, or `response` schema kinds.

Storage remains mapping-relative. A field is stored when a `StorageMapping` maps it. There is no universal `field.stored` Boolean.

## Value sources

`ValueSource` describes a neutral operation-backed collection used to discover valid values for a reference or interactive choice:

```text
ValueSource
├── operation
├── output
├── value_field
├── label_fields
└── optional search_input
```

A value source does not mean HTTP, SQL join, Mongo populate, React select, Flutter picker, or CLI prompt. Packs interpret it for their own target.

Core validation requires:

- referenced operation exists;
- named operation output exists and references a schema;
- value and label fields belong to that output schema;
- label fields are non-empty and unique.

Fixed selector:

```text
groups.value_sources.each
```

Template root:

```text
value_source
```

## Presentations

`Presentation` is a contract-level neutral application surface. It composes views from several groups without copying or re-owning them.

```text
Contract
├── groups
└── presentations
    └── entries
        └── view reference
```

Channels:

```text
web
mobile
desktop
command
document
conversational
```

A presentation owns:

- application-surface identity;
- channel;
- view placements;
- neutral address/route/command strings;
- navigation parent/order;
- tags, guidance, documentation, and provenance.

It does not own:

- React, Next.js, Flutter, GoRouter, Redux, Riverpod, CSS, widget trees, animations, or framework state management;
- visual layout pixels;
- target-language syntax.

A group owns what a view means. A presentation owns where that view participates in an application surface.

Fixed selectors:

```text
presentations.each
presentations.entries.each
```

Template roots:

```text
presentation
entry
```

## Selector registry implemented by the first orchestrator

The initial verified registry is intentionally small:

```text
groups.all
groups.each
groups.schemas.each
groups.schemas.objects.each
groups.schemas.enums.each
groups.operations.each
groups.views.each
groups.storage.mappings.each
groups.workflows.each
groups.policies.each
groups.events.each
groups.value_sources.each
presentations.each
presentations.entries.each
```

Selectors not listed above are not implemented and must not appear in pack guides or examples. In particular, the current runtime does not implement nested child selectors, DTO selectors, operation-input/output/failure selectors, arbitrary aliases, global reversed roots, filters, or graph-query grammar.

A future selector is added only through a typed core change with behavior versioning, validation, context preparation, tests, and documentation.

## Validation and transport

These additions participate in:

- semantic identity indexing;
- cross-reference validation;
- deterministic selectors;
- bounded render context preparation;
- canonical JSON/YAML transport;
- source-adapter loading;
- plan inspection and artifact explanation.

They are not stored in arbitrary `extensions` or `raw` values.

## Non-goals

This alignment does not introduce:

- entities or repositories as neutral roots;
- runtime predicates;
- database query ASTs;
- framework bindings keyed to semantic IDs;
- a generic expression language for business logic;
- automatic operation generation;
- a universal visual UI DSL;
- target-specific pack configuration in IR.
