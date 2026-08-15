# Task 06 — Complete StorageMapping, ValueSource, and View semantics

Status: [ ]
Owner: `packages/python/dryv`
Depends on: Task 05
Validation: semantic model tests, mapping tests, relationship tests

## Goal

Complete the canonical persistence and interaction concepts while keeping storage representation and user-facing interaction meaning separate from Schema.

## StorageMapping

`StorageMapping` maps a Schema into one concrete storage representation. It does not replace or subclass the Schema.

It may express:

```text
mapped Schema
store identity/kind
field mappings
storage-only fields
generated fields
computed fields
omitted semantic fields
primary keys
foreign/reference mappings
unique constraints
indexes
storage checks/defaults
relationship mappings
cascade/storage lifecycle facts
concurrency/version fields
serialization/embedded storage facts
```

### Semantic versus storage constraints

A rule that is meaningful regardless of persistence technology belongs to Schema/Policy semantics and may later be emitted as a storage check.

A persistence-specific constraint belongs only to StorageMapping.

Schema extension does not imply storage inheritance. Any storage reuse/inheritance strategy must be explicit in StorageMapping if later approved.

## ValueSource

`ValueSource` is a neutral candidate-value relationship reusable by web, mobile, CLI, docs, tests and conversational surfaces.

It may reference:

```text
source Operation
output collection/item
value field
label field(s)
optional search/query input
optional dependent inputs
```

It must not define a dropdown, HTTP fetch function or framework component.

## View

`View` is a Group-owned neutral interaction unit.

It may reference:

```text
Schemas it uses
field uses/parts
ValueSources
Operations it triggers
Workflows it triggers
Events it reacts to
Policies/access
connections to other Views
guidance/tags/provenance
```

A View is not inherently a page, screen, form, component, table, modal or CLI command. Packs decide emitted representations.

## Reverse relationships

Do not author duplicated reverse lists such as `Schema.storageMappings` or `Operation.triggeringViews` inside canonical source objects. The later IR Runtime Feature derives indexes for context and inspection.

## Non-goals

- Do not add ORM classes or SQL syntax to Schema.
- Do not implement database connections or migrations.
- Do not define frontend framework state/components.
- Do not implement pack selection vocabulary.

## Allowed paths

- `packages/python/dryv/src/dryv/ir/storage/**`
- `packages/python/dryv/src/dryv/ir/sources/**`
- `packages/python/dryv/src/dryv/ir/views/**`
- shared canonical refs/kernel files needed by these concepts
- corresponding tests/docs

## Acceptance criteria

- StorageMapping has explicit Schema linkage and portable typed storage facts.
- Storage-only fields/constraints can exist without polluting Schema.
- ValueSource references existing concepts rather than frontend mechanisms.
- View composes Schema/Operation/Event/Workflow/Policy/ValueSource relationships neutrally.
- All refs are validated and deterministic.

## Validation

Add tests for semantic/storage separation, generated/storage-only fields, constraints/indexes, ValueSource output/field refs, View triggers/reactions and invalid cross-reference cases. Run Dryv IR/architecture tests and `git diff --check`.
