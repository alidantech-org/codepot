# First reference delivery slice

## Purpose

The reference slice is the smallest complete product demonstration capable of proving Codepot’s distinctive value. It is intentionally narrower than the full semantic vision.

It must demonstrate repeated, safe evolution across several connected artifacts. A greenfield CRUD scaffold is not sufficient.

## Product statement

> Define a small service domain once, inspect compatibility and the complete derivation plan, and safely generate coordinated service, storage, SDK, and documentation artifacts through reusable packs.

## Reference domain

Use a realistic but bounded business domain with:

- two or three groups;
- several structural schemas;
- reusable constrained fields;
- references and one-to-many relationships;
- read and write operations;
- typed failures;
- HTTP and access facts;
- one domain event;
- one storage mapping with keys and indexes;
- one workflow or view only if required to prove a current contract.

A ticketing, booking, account, or small commerce domain is appropriate because it naturally exercises API, storage, client, and documentation concerns.

## Minimum semantic scope

### Contract and grouping

- contract identity and version;
- groups and ownership;
- documentation and source provenance;
- stable semantic IDs.

### Structural schemas

- primitives and constrained properties;
- enums;
- object schemas and fields;
- optionality and nullability;
- arrays and references;
- explicit derivation for create/read/update shapes;
- deterministic names and provenance.

### Operations

- typed inputs and outputs;
- named failures;
- read and write effects;
- HTTP facet;
- access policy reference;
- emitted event where relevant.

### Storage

- schema-to-store mapping;
- primary key;
- unique constraint;
- index;
- stored/generated/omitted field state;
- one relationship.

### Events and policies

- one event with payload;
- one public and one protected access policy;
- explicit operation relationships.

Do not require presentations, rich views, arbitrary workflows, scheduling, or advanced mappings unless they are already stable and directly needed by the reference projects.

## Input routes

Support two equal routes:

1. one language-native authoring frontend compiling to in-memory IR;
2. canonical JSON or YAML loaded by the runtime.

Both routes must produce equivalent canonical digest, plan, and artifacts.

A second authoring language is not required for the first slice, but the conformance corpus must be ready for it.

## Pack family

## Pack A — service/API boundary

Generates a target service structure containing:

- structural data types;
- operation input/output types;
- typed failure representations;
- handler/controller/resolver boundaries according to pack architecture;
- routing/transport declarations;
- validation declarations;
- extension interfaces or neighboring handwritten modules.

The pack does not generate custom business algorithms.

## Pack B — storage and migration

Generates:

- persistence mapping declarations;
- table/collection or equivalent schema;
- key, unique, index, and relation representation;
- one additive migration or migration descriptor;
- storage adapter boundary.

Storage syntax and architecture are pack decisions. Runtime IR remains mapping-oriented.

## Pack C — client SDK

Generates:

- public models;
- operation request and response types;
- client methods;
- error types;
- module exports;
- package metadata required by the pack.

It must consume the same operation and schema meaning as the service pack through independent templates.

## Pack D — documentation and trace

Generates or exposes:

- contract overview;
- schemas and operations;
- access/failure/event notes;
- compatibility summary;
- semantic-to-artifact links or trace references.

This pack proves that canonical meaning is useful beyond executable code.

## Cross-pack dependencies

The slice must exercise explicit generated dependencies:

- service operation artifact imports generated schema symbols;
- SDK client imports generated SDK model symbols;
- aggregate/barrel artifacts export per-item artifacts;
- documentation links to stable semantic identities;
- storage mapping refers to the same schema identity without becoming a global entity.

No pack may search rendered output to discover providers.

## Project configuration

The reference `dryv.yaml` should show clearly:

- contract source;
- four pack instances or an equivalent coherent composition;
- local pack sources first;
- explicit output roots;
- a small number of typed options;
- at least one project binding;
- command policy;
- frozen lock behavior after initial resolution.

The file should remain understandable without reading the pack manifests.

## Required evolution sequence

## Evolution 1 — add a field

Add a non-breaking optional field.

Expected effects:

- affected service and SDK types update;
- storage behavior follows explicit mapping policy;
- documentation updates;
- compatibility reports non-breaking;
- unaffected operations and artifacts remain explainably unchanged.

## Evolution 2 — add a required input field

Add a required field to a write input.

Expected effects:

- compatibility report identifies affected callers;
- service validation and SDK request update;
- storage update occurs only if mapping declares it;
- plan shows exact blast radius.

## Evolution 3 — rename while preserving identity

Rename a schema or field with explicit identity preservation.

Expected effects:

- semantic diff records rename rather than delete/create;
- target symbols and paths may change according to packs;
- stale generated artifacts are removed only when safe;
- compatibility consequences are target/policy-aware;
- trace links old and new provenance.

## Evolution 4 — add an operation

Add one protected operation with input, output, failure, and event effect.

Expected effects:

- service boundary, SDK, docs, and exports update;
- policy and event relationships validate;
- generated dependency graph resolves completely.

## Evolution 5 — deliberate breaking change

Remove or tighten a public field/operation.

Expected effects:

- compatibility detection blocks or warns according to policy;
- generation cannot hide the break;
- reviewed waiver is possible without changing detection;
- affected artifacts and consumers are listed.

## Evolution 6 — storage-only change

Add an index or change a mapping-specific storage fact.

Expected effects:

- storage/migration pack changes;
- service and SDK remain unchanged unless a semantic dependency exists;
- impact graph demonstrates separation of schema from storage mapping.

## Evolution 7 — pack upgrade

Change a pack version or commit.

Expected effects:

- lock change is explicit;
- plan explains artifacts affected by template/behavior changes;
- project-owned handwritten code remains intact;
- generated target verification passes.

## Evolution 8 — manual-edit conflict

Edit one managed generated file deliberately.

Expected effects:

- generation refuses silent overwrite;
- plan/state identifies original and current digests;
- recovery choices are clear;
- other files remain unchanged after failed generation.

## Evolution 9 — semantic removal and stale cleanup

Remove an obsolete operation or schema.

Expected effects:

- dependency checks prevent unsafe removal;
- unchanged stale managed artifacts are removed;
- edited stale artifacts are protected;
- ownership state updates transactionally.

## Evolution 10 — clean reproduction

Clone or copy only authored source, project configuration, lock, packs, and required handwritten files into a clean supported environment.

Expected effects:

- canonical, plan, and artifact digests match;
- generated targets validate;
- no hidden local registry or cache is required.

## Handwritten code boundary

The reference service includes at least one handwritten business implementation that depends on generated contracts through an explicit extension point.

The evolution sequence must prove:

- generated regeneration does not overwrite it;
- pack upgrades preserve the boundary;
- the compiler/test suite catches incompatible generated contract changes;
- trace identifies the generated provider but does not claim ownership of handwritten logic.

## Plan and explanation demonstration

Before every evolution, the user can answer:

- What semantic facts changed?
- Is the change compatible?
- Which pack selections are invoked?
- Which templates are selected or skipped?
- Which artifacts add, update, remove, or remain unchanged?
- Which dependencies provide imports/exports?
- Which commands require approval?
- Which managed files are protected?
- Why is each destination chosen?

After generation, the user can trace any file back to semantic identities and pack origins.

## Generated-target verification

The reference workflow includes target-native verification appropriate to each pack:

- compile/type-check;
- lint/format check;
- generated tests;
- minimal service runtime or contract check;
- SDK/service interoperability;
- migration validation;
- documentation link validation;
- deterministic rerun.

Codepot runtime tests alone do not satisfy this requirement.

## Human and agent demonstration

Run one evolution twice:

### Human route

A developer changes authoring or canonical IR, validates, reviews the plan, generates, and verifies.

### Agent route

An AI agent uses public runtime operations to inspect, propose a semantic change, validate, review structured diagnostics/plan, generate according to policy, and report trace/verification.

Compare results with an agent that edits the repository directly.

## Baseline comparison

Measure the same evolution sequence using:

1. ordinary API/schema/ORM tools plus manual edits;
2. direct AI repository editing;
3. Codepot-assisted human workflow;
4. Codepot-assisted hybrid agent workflow.

Record:

- active and elapsed time;
- artifacts missed;
- inconsistencies;
- review and correction time;
- tests and failures;
- manual generated-file edits;
- runtime/pack maintenance effort;
- agent tokens/tool calls;
- confidence and explanation quality.

## Success criteria

The reference slice succeeds when:

- all outputs derive from one canonical contract;
- full plans are stable and explainable;
- generated dependencies are explicit;
- repeated evolution is safer and faster for the selected domain;
- generated and handwritten ownership remains comfortable;
- compatibility issues are caught before mutation;
- failure and conflict do not lose user work;
- clean reproduction works across supported platforms;
- the same packs work in two independent projects;
- agent use reduces unintended or inconsistent edits;
- maintenance cost is included and acceptable.

## Failure and narrowing criteria

Narrow the product if:

- most value comes only from one pack;
- the kernel needs target-specific concepts;
- every evolution requires pack modification;
- custom logic repeatedly enters managed files;
- plans are too complex for developers to review;
- Codepot is slower with no meaningful safety gain;
- agent workflows bypass or misunderstand the runtime;
- pack maintenance exceeds repeated project savings.

## What comes after the slice

Only after successful evidence should the team consider:

- another authoring language;
- views and presentations;
- richer workflows and policies;
- another target stack;
- conservative incremental generation;
- organizational policy services;
- pack catalog or marketplace;
- native Codepot language.

The reference slice is not a demo milestone. It is the decision point that determines whether the architecture should expand.
