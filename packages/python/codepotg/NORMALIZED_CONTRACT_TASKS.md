# CodepotG Normalized Contract Tasks

Branch: `chatgpt/codepotx-restart`

Status legend:

```text
[ ] not started
[-] in progress
[x] complete
[!] blocked or requires documented decision
```

## Goal

Expand CodepotG into a complete, lossless, language-neutral OpenAPI and `x-codegen` generation contract while preserving the current package architecture, public variables, adapters, templates, configuration, CLI, inference boundaries, and emission behavior.

The resulting Jinja contract must make template composition direct and predictable. Known facts use named normalized variables; unknown and not-yet-normalized facts remain preserved through extensions and raw source objects. No source value may be silently discarded.

## Locked design rules

- [x] Preserve the existing pipeline: loader -> inference -> API contract -> template contract -> adapter -> Jinja -> emission.
- [x] Keep language-neutral contracts free of target-language syntax.
- [x] Add before replacing; alias before deprecating; do not remove current public paths in this work.
- [x] Keep existing TypeScript, Next.js, Dart, debug, custom-pack, path, import, write-policy, CLI, and release behavior working.
- [x] Preserve OpenAPI 3.0 and 3.1 support.
- [x] Preserve original refs after resolution.
- [x] Distinguish missing values from explicit `null`.
- [x] Normalize known `x-codegen` information into fixed structures.
- [x] Preserve unknown extensions and complete raw source objects.
- [x] Do not add fixture generation or runtime mock-server behavior.
- [x] Treat every programming language and deterministic text format as adapter scope without discrimination.

## Documentation gate

- [x] Add `docs/README.md`.
- [x] Add `docs/template-authoring.md`.
- [x] Add `docs/template-variables.md`.
- [x] Add `docs/normalized-contract.md`.
- [x] Add `docs/x-codegen-metadata.md`.
- [x] Add `docs/openapi-preservation.md`.
- [x] Add `docs/language-adapters.md`.
- [x] Add `docs/compatibility.md`.
- [ ] Link the documentation index from the package README.
- [ ] Add documentation checks for broken relative links.

---

# Phase 0 — Establish the compatibility baseline

## 0.1 Record branch and package state

- [ ] Record the exact starting branch head in this file.
- [ ] Inventory package modules under `src/contracts`, `src/inference`, `src/languages`, `src/emission`, `src/openapi`, and tests.
- [ ] Inventory all bundled template packs and their `paths.yaml` files.
- [ ] Inventory every current global and contextual template variable.
- [ ] Inventory existing metadata dictionaries and compatibility paths.

Completion criteria:

```text
baseline commit recorded
current public variables listed
current bundled packs listed
no implementation changes included
```

## 0.2 Run the existing validation suite

- [ ] Run the package test suite.
- [ ] Run Ruff.
- [ ] Run build and package validation where available.
- [ ] Run CLI startup checks.
- [ ] Generate representative TypeScript, Next.js, Dart, and debug output.
- [ ] Save stable snapshots or hashes for representative output.
- [ ] Document every pre-existing failure before changing implementation.

Completion criteria:

```text
baseline test state documented
baseline generated output captured
pre-existing failures separated from new failures
```

Commit boundary:

```text
test(codepotg): lock normalized contract compatibility baseline
```

---

# Phase 1 — Add lossless source foundations

## 1.1 Shared preservation concepts

- [ ] Add a common extension map contract.
- [ ] Add a common raw source map contract.
- [ ] Add a presence-aware value contract with `value`, `is_set`, and origin.
- [ ] Add value origins for authored, inferred, derived, and effective values.
- [ ] Add a normalized diagnostic contract.
- [ ] Add diagnostic categories for unresolved, raw-only, unsupported, malformed, deprecated, and lost values.
- [ ] Add ordered named-note structures for unknown information-note categories.

Compatibility requirements:

- Existing values remain available at their current paths.
- Existing `meta` dictionaries remain populated.
- New structures are additive.

## 1.2 Preserve the complete document

- [ ] Retain the complete loaded OpenAPI root in the inference graph.
- [ ] Expose the complete root as `api.raw`.
- [ ] Preserve root unknown `x-*` values as `api.extensions`.
- [ ] Preserve OpenAPI dialect information.
- [ ] Preserve root security, tags, external docs, webhooks, and all component registries.
- [ ] Ensure raw data is read-only from template perspective.

## 1.3 Object-level preservation

Add raw and extension preservation for:

- [ ] document information;
- [ ] servers;
- [ ] path items;
- [ ] resources;
- [ ] schemas;
- [ ] fields;
- [ ] operations;
- [ ] parameters;
- [ ] request bodies;
- [ ] responses;
- [ ] media types;
- [ ] headers;
- [ ] examples;
- [ ] links;
- [ ] callbacks;
- [ ] security schemes;
- [ ] entities;
- [ ] entity fields;
- [ ] relations;
- [ ] constraints;
- [ ] access policies;
- [ ] hooks;
- [ ] frontends;
- [ ] screens;
- [ ] components.

Tests:

- [ ] unknown extension preserved;
- [ ] unknown standard-looking key preserved and diagnosed;
- [ ] explicit null retained;
- [ ] original ref retained after resolution;
- [ ] malformed value retained and diagnosed;
- [ ] no loss diagnostics for the shared real OpenAPI contract.

Commit boundary:

```text
feat(codepotg): preserve OpenAPI source objects losslessly
```

---

# Phase 2 — Normalize references, values, collections, and notes

## 2.1 References

- [ ] Add one shared reference shape.
- [ ] Preserve `ref`, kind, name, owner, resolution state, and target.
- [ ] Support schema, resource, entity, operation, component, access-policy, hook, frontend, and unknown reference kinds.
- [ ] Resolve references only after the target registry exists.
- [ ] Support circular references without recursive object expansion.
- [ ] Add unresolved-reference diagnostics with source paths.

## 2.2 Schema-use contract

- [ ] Add one schema-use shape for refs, multiple refs, resolved schemas, and inline schemas.
- [ ] Use it for fields, parameters, media types, array items, composition branches, additional properties, frontend props, and entity links.
- [ ] Retain current `schema_ref`, `schema_refs`, `item_ref`, and `item_refs` compatibility fields.

## 2.3 Collection contract

- [ ] Add deterministic collection wrappers.
- [ ] Expose `all`, `count`, `by_id`, and `by_name`.
- [ ] Preserve tuples as the authoritative ordered sequence.
- [ ] Add classified views without duplicating inference.
- [ ] Add collision diagnostics for duplicate ids or names.

## 2.4 Structured information notes

Normalize:

- [ ] explain;
- [ ] access;
- [ ] implement;
- [ ] validation;
- [ ] security;
- [ ] observability;
- [ ] UX;
- [ ] performance;
- [ ] testing;
- [ ] unknown named categories under `other`.

Commit boundary:

```text
feat(codepotg): add shared normalized contract primitives
```

---

# Phase 3 — Complete primitive and JSON Schema metadata

## 3.1 Primitive identity

- [ ] Preserve source `type` as one or more values.
- [ ] Preserve normalized resolved type.
- [ ] Preserve source and resolved format.
- [ ] Normalize nullable behavior across OpenAPI 3.0 and 3.1.
- [ ] Preserve source representation and effective meaning.

## 3.2 Presence-aware values

- [ ] Normalize default.
- [ ] Normalize const.
- [ ] Normalize example and examples.
- [ ] Distinguish absent, null, false, zero, empty string, and empty collections.
- [ ] Keep existing simple default fields as compatibility aliases.

## 3.3 Numeric constraints

- [ ] minimum;
- [ ] maximum;
- [ ] exclusive minimum;
- [ ] exclusive maximum;
- [ ] multiple of.

## 3.4 String constraints

- [ ] minimum length;
- [ ] maximum length;
- [ ] pattern;
- [ ] content encoding;
- [ ] content media type;
- [ ] content schema.

## 3.5 Array constraints

- [ ] items;
- [ ] prefix items;
- [ ] contains;
- [ ] minimum contains;
- [ ] maximum contains;
- [ ] minimum items;
- [ ] maximum items;
- [ ] unique items;
- [ ] unevaluated items.

## 3.6 Object constraints

- [ ] properties;
- [ ] required;
- [ ] additional properties with allowed, forbidden, typed, and referenced states;
- [ ] pattern properties;
- [ ] property names;
- [ ] minimum properties;
- [ ] maximum properties;
- [ ] dependent required;
- [ ] dependent schemas;
- [ ] unevaluated properties.

## 3.7 Composition and conditions

- [ ] allOf branches;
- [ ] anyOf branches;
- [ ] oneOf branches;
- [ ] not schema;
- [ ] if schema;
- [ ] then schema;
- [ ] else schema;
- [ ] references and inline branches;
- [ ] discriminator metadata;
- [ ] inherited-ref compatibility views.

## 3.8 Annotations

- [ ] title;
- [ ] summary where supported;
- [ ] description;
- [ ] read only;
- [ ] write only;
- [ ] deprecated;
- [ ] external docs;
- [ ] JSON Schema ids, anchors, dynamic anchors, refs, and dialect.

Tests:

- [ ] complete Zod-relevant constraint fixture;
- [ ] explicit-null default;
- [ ] inline anyOf and oneOf;
- [ ] tuple schema through prefix items;
- [ ] strict and open objects;
- [ ] recursive schema;
- [ ] OpenAPI 3.0 and 3.1 equivalent normalization;
- [ ] no primitive metadata loss in the shared contract.

Commit boundaries:

```text
feat(codepotg): normalize schema values and primitive constraints
feat(codepotg): normalize arrays objects and compositions
```

---

# Phase 4 — Complete HTTP and OpenAPI operation contracts

## 4.1 Document and server information

- [ ] contact;
- [ ] license;
- [ ] terms of service;
- [ ] external docs;
- [ ] server variables and source metadata.

## 4.2 Security

- [ ] root security requirements;
- [ ] operation security overrides;
- [ ] explicit public operations using an empty security list;
- [ ] API key schemes;
- [ ] HTTP schemes;
- [ ] mutual TLS;
- [ ] OAuth flows and scopes;
- [ ] OpenID Connect;
- [ ] resolved scheme references.

## 4.3 Path items

- [ ] path summary and description;
- [ ] path parameters;
- [ ] operation parameters;
- [ ] declared and effective parameter views;
- [ ] path servers;
- [ ] path extensions and raw source.

## 4.4 Parameters

- [ ] description;
- [ ] deprecation;
- [ ] style;
- [ ] explode;
- [ ] allow empty value;
- [ ] allow reserved;
- [ ] examples;
- [ ] schema use;
- [ ] content-based parameters.

## 4.5 Request bodies and media types

- [ ] description;
- [ ] required;
- [ ] media schemas;
- [ ] examples;
- [ ] encoding;
- [ ] headers per encoding;
- [ ] normalized primary request-body helpers.

## 4.6 Responses

- [ ] status code and ranges;
- [ ] description;
- [ ] media schemas;
- [ ] examples;
- [ ] headers;
- [ ] links;
- [ ] success and error classification;
- [ ] primary response selection;
- [ ] default response support.

## 4.7 Remaining operation facts

- [ ] callbacks;
- [ ] webhooks;
- [ ] operation external docs;
- [ ] servers;
- [ ] deprecated;
- [ ] tags;
- [ ] summary and description;
- [ ] stable operation target metadata.

Commit boundary:

```text
feat(codepotg): normalize complete OpenAPI operation contracts
```

---

# Phase 5 — Normalize resources and operation `x-codegen`

## 5.1 Resources

- [ ] normalize route;
- [ ] normalize tags;
- [ ] normalize UI settings;
- [ ] link access policies;
- [ ] link hook definitions;
- [ ] attach operations;
- [ ] attach schemas;
- [ ] attach entities;
- [ ] normalize structured notes;
- [ ] expose resource classified collections.

## 5.2 Operation identity and UI

- [ ] normalize operation name;
- [ ] normalize authored or inferred role;
- [ ] preserve role origin;
- [ ] normalize authored tags;
- [ ] normalize UI enabled, infer, inferred, role, source, and reason;
- [ ] compute effective resource-plus-operation UI values.

## 5.3 Parameter targets

- [ ] normalize combined query or params target;
- [ ] resolve target schema;
- [ ] expose query, params, body, and response convenience schemas;
- [ ] preserve individual OpenAPI parameters.

## 5.4 Data sources

- [ ] normalize named sources;
- [ ] resolve item schemas;
- [ ] normalize response field, key, label, and value fields;
- [ ] expose deterministic source collections;
- [ ] select primary source without discarding others.

Commit boundary:

```text
feat(codepotg): normalize resource and operation metadata
```

---

# Phase 6 — Normalize cache, access, runtime, and hooks

## 6.1 Cache

- [ ] normalize cache enabled state;
- [ ] normalize read policy;
- [ ] normalize TTL, stale time, scope, key fields, and tags;
- [ ] normalize operation invalidation names;
- [ ] resolve invalidated operations;
- [ ] normalize resource invalidation names and targets;
- [ ] normalize tag invalidation;
- [ ] support invalidate-all;
- [ ] diagnose unknown targets without data loss.

## 6.2 Access definitions

- [ ] normalize global policies;
- [ ] normalize resource-scoped policies;
- [ ] normalize context references;
- [ ] normalize role requirements;
- [ ] normalize permission requirements;
- [ ] normalize public and authenticated behavior;
- [ ] preserve policy notes and extensions.

## 6.3 Access use

- [ ] retain source policy ref;
- [ ] resolve operation policy;
- [ ] expose resolution state;
- [ ] preserve unresolved use and diagnostics.

## 6.4 Runtime transport

- [ ] inbound IP requirement;
- [ ] inbound user-agent requirement;
- [ ] inbound header requirements;
- [ ] inbound cookie requirements;
- [ ] outbound cookie behavior;
- [ ] outbound header behavior.

## 6.5 Hook definitions and uses

- [ ] normalize resource hook definitions;
- [ ] normalize before-handler uses;
- [ ] normalize after-success uses;
- [ ] normalize after-error uses;
- [ ] preserve source order;
- [ ] resolve hooks after resource registries exist;
- [ ] diagnose unknown hooks.

Commit boundaries:

```text
feat(codepotg): normalize cache and access policies
feat(codepotg): normalize runtime transport and hooks
```

---

# Phase 7 — Normalize entities and persistence rules

## 7.1 Base entities

- [ ] normalize root base-entity registry;
- [ ] use the same contract as concrete entities;
- [ ] normalize abstract kind and visibility;
- [ ] resolve base-entity inheritance;
- [ ] support inheritance chains and cycles diagnostics.

## 7.2 Entity identity and storage

- [ ] resource reference;
- [ ] schema reference;
- [ ] store or table identity;
- [ ] kind;
- [ ] abstract flag;
- [ ] visibility;
- [ ] structured notes;
- [ ] extensions and raw source.

## 7.3 Field inheritance

- [ ] declared fields;
- [ ] inherited fields;
- [ ] effective fields;
- [ ] override detection;
- [ ] override origin;
- [ ] deterministic field order;
- [ ] duplicate-field diagnostics.

## 7.4 Entity field behavior

- [ ] schema use and normalized type;
- [ ] constraints and defaults;
- [ ] role;
- [ ] generated behavior;
- [ ] uniqueness;
- [ ] index behavior;
- [ ] readonly;
- [ ] editable;
- [ ] managed;
- [ ] immutable;
- [ ] selectable;
- [ ] backend-only;
- [ ] authored-versus-effective flags.

## 7.5 Query capabilities

- [ ] exact;
- [ ] one-of;
- [ ] sort;
- [ ] select;
- [ ] date;
- [ ] range;
- [ ] prefix search;
- [ ] contains search;
- [ ] fuzzy search;
- [ ] derived operator collection;
- [ ] unknown operator preservation.

## 7.6 Backend fields and visibility views

- [ ] normalize backend fields as entity fields;
- [ ] keep public and backend views separate;
- [ ] expose storage fields;
- [ ] expose editable, readonly, and queryable views;
- [ ] prevent frontend packs from receiving backend-only fields through public views.

## 7.7 Relations

- [ ] cardinality;
- [ ] target entity ref and resolution;
- [ ] local fields as an ordered collection;
- [ ] foreign fields as an ordered collection;
- [ ] delete action;
- [ ] update action;
- [ ] nullable;
- [ ] owning side;
- [ ] inverse field;
- [ ] to-one and to-many helpers;
- [ ] composite-key support.

## 7.8 Constraints and rules

- [ ] index constraints;
- [ ] unique constraints;
- [ ] ordered field lists;
- [ ] recursive rule-expression contract;
- [ ] `when` rules;
- [ ] equality rules;
- [ ] not-null rules;
- [ ] general argument support;
- [ ] unknown operation preservation;
- [ ] raw rule arguments and diagnostics.

Commit boundaries:

```text
feat(codepotg): normalize base entities and field inheritance
feat(codepotg): normalize entity behavior relations and constraints
```

---

# Phase 8 — Normalize schema-specific `x-codegen`

- [ ] kind;
- [ ] resource;
- [ ] role;
- [ ] shared;
- [ ] projection source;
- [ ] projection include;
- [ ] projection exclude;
- [ ] projection rename;
- [ ] projection partial behavior;
- [ ] request, response, query, params, body, model, DTO, enum, primitive, and unknown role helpers;
- [ ] preserve current schema groups and emission groups.

Commit boundary:

```text
feat(codepotg): normalize schema roles and projections
```

---

# Phase 9 — Normalize frontends

## 9.1 Frontend definition

- [ ] id and name;
- [ ] title;
- [ ] route prefix;
- [ ] folders;
- [ ] components;
- [ ] screens;
- [ ] linked operations;
- [ ] linked schemas;
- [ ] notes, extensions, and raw source.

## 9.2 Components

- [ ] props schema use;
- [ ] schema uses;
- [ ] operation uses;
- [ ] aliases and purposes;
- [ ] tags;
- [ ] notes;
- [ ] resolved operation and schema targets.

## 9.3 Screens

- [ ] route;
- [ ] full route;
- [ ] params schema;
- [ ] query schema;
- [ ] component placement;
- [ ] operation uses;
- [ ] aliases and purposes;
- [ ] tags and notes.

## 9.4 Selection compatibility

- [ ] preserve one-frontend selection;
- [ ] preserve wildcard all-frontends selection;
- [ ] preserve explicitly authored-only behavior;
- [ ] preserve selected frontend aliases and count.

Commit boundary:

```text
feat(codepotg): normalize frontend screens components and uses
```

---

# Phase 10 — Build the final template-variable contract

## 10.1 Canonical root and aliases

- [ ] expose the complete canonical `api` root;
- [ ] preserve current top-level aliases;
- [ ] add `access` alias;
- [ ] ensure alias identity or value equivalence;
- [ ] document stable versus compatibility paths.

## 10.2 Contextual variables

- [ ] resource;
- [ ] schema;
- [ ] model;
- [ ] DTO;
- [ ] enum;
- [ ] primitive;
- [ ] operation;
- [ ] field;
- [ ] parameter;
- [ ] request and request body;
- [ ] response;
- [ ] entity;
- [ ] relation;
- [ ] constraint;
- [ ] frontend;
- [ ] screen;
- [ ] component.

## 10.3 Classified collections

Add and test every collection documented in `docs/template-variables.md`.

## 10.4 Safe empty values

- [ ] no optional metadata causes template attribute errors;
- [ ] missing collections are iterable;
- [ ] missing lookups are empty;
- [ ] explicit-null values remain distinguishable;
- [ ] unresolved targets remain inspectable.

## 10.5 Debug contract output

- [ ] print global variable inventory;
- [ ] print contextual variable inventory;
- [ ] print normalized facts;
- [ ] print resolved references;
- [ ] print extensions;
- [ ] print raw-only paths;
- [ ] print diagnostics;
- [ ] print loss count.

Commit boundary:

```text
feat(codepotg): expose complete normalized Jinja contract
```

---

# Phase 11 — Migrate existing adapters and packs safely

## 11.1 TypeScript

- [ ] migrate to normalized schema constraints;
- [ ] generate complete Zod-compatible validation facts;
- [ ] preserve current types and output paths;
- [ ] use normalized operation, cache, access, entity, and frontend data;
- [ ] compare snapshots.

## 11.2 Next.js

- [ ] preserve current Next.js profile behavior;
- [ ] adopt normalized routes, UI, frontends, access, cache, and sources;
- [ ] compare snapshots.

## 11.3 Dart

- [ ] adopt normalized values and constraints;
- [ ] preserve null-safety and current output;
- [ ] compare snapshots.

## 11.4 Debug

- [ ] become the canonical contract-completeness report;
- [ ] expose all documented variables;
- [ ] report raw-only and loss values.

## 11.5 Custom packs

- [ ] smoke-test a project-owned pack using only current variables;
- [ ] smoke-test a project-owned pack using normalized variables;
- [ ] verify both work in the same release.

Commit boundaries:

```text
refactor(codepotg): migrate TypeScript and Next packs to normalized contracts
refactor(codepotg): migrate Dart and debug packs to normalized contracts
```

---

# Phase 12 — Universal language-adapter implementation

Every language and deterministic text format listed in `docs/language-adapters.md` is committed scope. The registry remains open for newly created languages. No language family is excluded or treated as less eligible.

## 12.1 Universal adapter test kit

- [ ] canonical name and aliases;
- [ ] reserved words;
- [ ] naming and file naming;
- [ ] primitive types;
- [ ] arrays, maps, tuples, objects, unions, intersections, enums, and recursion;
- [ ] nullable and optional values;
- [ ] defaults, constants, examples, and literals;
- [ ] validation constraints;
- [ ] imports and dependencies;
- [ ] comments and documentation;
- [ ] formatting and post-actions;
- [ ] representative generated output;
- [ ] real shared-contract generation.

## 12.2 Implement all adapter categories in order

- [ ] web and JavaScript ecosystem;
- [ ] Python ecosystem;
- [ ] JVM ecosystem;
- [ ] .NET ecosystem;
- [ ] native and systems languages;
- [ ] Apple ecosystem;
- [ ] mobile and cross-platform languages;
- [ ] functional languages;
- [ ] dynamic and scripting languages;
- [ ] Ruby ecosystem;
- [ ] PHP ecosystem;
- [ ] BEAM ecosystem;
- [ ] Go ecosystem;
- [ ] Rust ecosystem;
- [ ] C and C++ ecosystem;
- [ ] scientific and data languages;
- [ ] legacy and enterprise languages;
- [ ] logic, theorem, and rule languages;
- [ ] smart-contract and blockchain languages;
- [ ] database and query languages;
- [ ] schema and interface languages;
- [ ] serialization and data formats;
- [ ] documentation and publishing formats;
- [ ] markup and styling languages;
- [ ] shell and command languages;
- [ ] infrastructure and operations formats;
- [ ] CI, build, and package formats;
- [ ] editor, lint, and tooling formats;
- [ ] API testing and client collection formats;
- [ ] observability and policy formats;
- [ ] game and engine ecosystems;
- [ ] hardware and embedded languages;
- [ ] domain-specific and generated artifacts;
- [ ] every new language added to the universal registry after this catalog.

## 12.3 Language profiles

For every applicable language, implement packs for:

- [ ] plain models;
- [ ] runtime validation;
- [ ] client SDK;
- [ ] server interfaces;
- [ ] framework integration;
- [ ] persistence or ORM;
- [ ] UI bindings;
- [ ] documentation;
- [ ] configuration;
- [ ] schemas and migrations.

## 12.4 Adapter isolation

- [ ] no adapter parses raw OpenAPI for supported facts;
- [ ] no adapter modifies the language-neutral contract;
- [ ] missing language-neutral needs produce additive contract proposals;
- [ ] existing adapters remain green after each new adapter;
- [ ] adapters are discoverable without central hard-coded discrimination.

Commit policy:

```text
one coherent adapter or closely related profile family per commit
shared adapter infrastructure in separate commits
snapshot and real-contract tests in the same commit as each adapter
```

---

# Phase 13 — Completeness and release gates

## 13.1 Shared real-contract audit

Run the supplied complete OpenAPI contract and report:

```text
typed values
resolved references
preserved extensions
preserved raw-only values
unsupported but preserved values
malformed but preserved values
lost values
```

Required result:

```text
lost values = 0
unresolved internal references = 0
```

## 13.2 Compatibility gate

- [ ] existing tests pass;
- [ ] Ruff passes;
- [ ] build and wheel validation pass;
- [ ] CLI startup passes;
- [ ] TypeScript output remains compatible;
- [ ] Next.js output remains compatible;
- [ ] Dart output remains compatible;
- [ ] debug output is complete;
- [ ] legacy custom pack works;
- [ ] normalized custom pack works;
- [ ] OpenAPI 3.0.3 test passes;
- [ ] OpenAPI 3.1.0 test passes;
- [ ] documentation links pass;
- [ ] no loss diagnostics.

## 13.3 Documentation gate

- [ ] every stable variable is documented;
- [ ] every collection view is documented;
- [ ] every compatibility alias is documented;
- [ ] every adapter is listed in the registry documentation;
- [ ] every unsupported but preserved OpenAPI keyword is listed in debug output;
- [ ] no Python implementation examples appear in the template-authoring guides.

## 13.4 Release decision

A release is blocked when:

```text
existing output breaks without an approved compatibility path
a bundled adapter fails
an internal reference remains unresolved
a source value is lost
a documented variable is absent
a raw-only value is neither preserved nor diagnosed
package validation fails
```

---

# Required working discipline

For every implementation batch:

1. read the affected inference, contract, adapter, template, and test files;
2. add or update focused tests first where practical;
3. make the smallest additive contract change;
4. preserve current aliases;
5. update the debug contract output;
6. run focused tests;
7. run the complete package suite;
8. run Ruff;
9. compare generated output;
10. update this task file and affected documentation;
11. commit a coherent reversible batch.

Do not combine unrelated refactors with normalized-contract work.
