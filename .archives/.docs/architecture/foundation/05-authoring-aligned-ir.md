# Authoring-aligned closed IR additions

## One compilation target

Every authoring frontend produces the same public immutable `dryv.ir.Contract`:

```text
Python dryv-author ------------+
Canonical IR JSON/YAML --------+--> Contract
Future native Codepot language +
```

Pydantic models, decorators, builder objects, Python functions, ref registries, provider objects, and authoring projections never enter the IR or render contexts.

The following concepts are core-owned, typed, immutable, source-neutral, and transported through the canonical Dryv format:

- namespaced tags and categorized guidance;
- field lifecycle, query, and reference capabilities;
- operation-backed value sources;
- contract-level presentations and view placements.

## Tags

`KernelData.tags` is an immutable sorted `TagSet`.

Grammar:

```text
segment(:segment)*
segment = [a-z][a-z0-9_-]*
```

Tags are Boolean namespaced hints. They may influence pack/template behavior but do not create relationships, replace typed fields, add selectors, register context roots, carry arbitrary values, or contain source code.

Safe template calls on verified tag records:

```text
has
has_any
has_all
under
empty
```

Typed semantics remain authoritative. Requiredness, nullability, references, and access must not be encoded as tags when public typed fields exist.

## Categorized guidance

`KernelData.guidance` contains unique `GuidanceNote` values with a closed `GuidanceKind` such as:

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

Guidance explains intent to developers, reviewers, documentation packs, templates, and AI tools. It never silently creates behavior.

## Field capabilities

A schema remains structural. `SchemaField.capabilities` contains reusable neutral intent:

```text
FieldCapabilities
├── lifecycle
│   ├── initialize
│   ├── mutate
│   └── visibility
├── query
│   ├── operators
│   ├── sortable
│   └── selectable
└── reference
    ├── target_schema
    └── target_field
```

These facts do not automatically create operations, storage, repositories, forms, controls, or target syntax. Storage remains mapping-relative; there is no universal stored-field flag.

Authoring may derive ordinary structural schemas from capabilities when derivation is explicit, deterministic, and inspectable.

## Value sources

A `ValueSource` describes a neutral operation-backed collection used to discover candidate values:

```text
ValueSource
├── operation
├── output
├── value_field
├── label_fields
└── optional search_input
```

The same source may inform web controls, mobile pickers, CLI prompts, generated tests, or documentation. It does not prescribe transport, persistence, or UI implementation.

Core validation requires all referenced operations, outputs, schemas, and fields to exist and agree.

Fixed selector:

```text
groups.value_sources.each
```

## Presentations

A `Presentation` is a contract-level neutral application surface. It composes views from several groups without copying or re-owning them.

```text
Contract
├── groups
└── presentations
    └── entries
        └── view reference
```

Supported neutral channels include web, mobile, desktop, command, document, and conversational surfaces.

A presentation may describe identity, channel, view placement, neutral addresses, navigation relationships, tags, guidance, documentation, and provenance. It never contains framework components, pixel layout, target syntax, or runtime state-management details.

Fixed selectors:

```text
presentations.each
presentations.entries.each
```

## Current selector registry

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

Unlisted selectors are unsupported. A new selector requires a typed core change, behavior versioning, validation, context preparation, tests, and documentation.

## Validation and transport

These concepts participate in semantic indexing, cross-reference validation, selectors, prepared contexts, canonical JSON/YAML transport, planning, and artifact explanation. They are never hidden in arbitrary extension or raw-value bags.

## Non-goals

This alignment does not introduce:

- entities or repositories as neutral roots;
- runtime predicates or database query ASTs;
- framework bindings keyed directly to semantic IDs;
- arbitrary business-logic expression languages;
- automatic operation generation;
- a universal visual UI DSL;
- target-specific configuration inside IR.
