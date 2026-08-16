# Canonical Dryv Runtime IR

Canonical Dryv Runtime IR is the only semantic authority shared by every Author Backend, Runtime, pack, client, and AI agent.

## Ownership hierarchy

```text
Contract
└── Group
    ├── Property
    ├── Schema
    ├── Operation
    ├── Policy
    ├── Failure
    ├── Event
    ├── StorageMapping
    ├── ValueSource
    ├── View
    └── Workflow

Contract
└── Presentation
```

Groups own software concepts. Runtime validates semantic IDs and typed references and derives reverse indexes without writing duplicated authored state back into the contract.

## Contract and Group

A `Contract` is the root semantic document. `Group` organizes related software meaning and establishes explicit ownership. Nested groups remain semantic groups; pack/project output folders are separate generation concerns.

## Property

A `Property` represents reusable typed semantic property meaning. It is not a generated target-language property declaration.

## Schema and fields

`Schema` defines a data shape using typed `SchemaField` records and field capabilities/constraints.

Dryv supports the approved **single-base Schema extension** model:

```text
BaseRecord
    ↑
User
```

Runtime exposes both:

- the direct authored Schema;
- the effective Schema after the extension chain is resolved;
- provenance identifying where inherited fields/facts originated.

Extension cycles and invalid overrides are validation errors.

Fields may carry behavior such as visibility, write/query/reference capability, lifecycle facts, constraints, and typed references. These are semantic facts, not target-language syntax.

## Policy, Failure, Event, Operation

`Policy` describes semantic policy meaning.

`Failure` describes explicit failure meaning that Operations/Workflows may reference.

`Event` describes domain/system event meaning.

`Operation` describes behavior and explicit relations such as subjects, inputs, outputs, failures, emitted events, consumed/listened events, and approved facets.

Authoring records the forward relationship. Runtime derives reverse indexes such as:

```text
Operation emits Event
    → Event.emitters

Operation listens to Event
    → Event.listeners

Operation uses Schema
    → Schema.operations
```

The reverse relationship is inspection/planning data, not duplicated authored state.

## StorageMapping

`StorageMapping` relates a Schema to persistence/storage facts without turning the Schema itself into a framework-specific entity model.

Runtime derives:

```text
StorageMapping maps Schema
    → Schema.storageMappings
```

A pack may render that neutral mapping as a TypeORM entity, Django model, SQL DDL, documentation, or another target artifact. The generated vocabulary belongs to the pack/template.

## ValueSource

`ValueSource` describes where a semantic value originates and its explicit dependencies. Runtime validates those references and includes them in relevant semantic dependency graphs.

## View and Presentation

`View` represents neutral presentation/view meaning and typed connections/triggers/reactions.

`Presentation` organizes Views into a presentation/channel structure. Runtime derives reverse placement indexes such as:

```text
View placed in Presentation
    → View.presentations
```

## Workflow

`Workflow` describes multi-step semantic behavior, transitions, decisions, compensation, triggers, failures and approved facets. Workflow step identities/references participate in Runtime validation and dependency indexing.

## Cross-cutting semantic facts

Canonical records may carry:

- stable `SemanticId` references;
- names/projections;
- tags;
- documentation;
- guidance notes;
- provenance/source locations;
- approved facets;
- typed type expressions.

These facts remain language/framework/runtime neutral.

## Serialization

The Runtime Serialization Feature owns deterministic representation mechanics for:

```text
JSON
YAML
JSONL canonical records
```

Equivalent canonical values serialize/hash deterministically. Author implementations define meaning; they do not create a second semantic model.

## Validation and indexing

`dryv.features.ir` owns runtime validation/indexing over canonical objects:

- duplicate IDs;
- invalid/missing typed references;
- ownership consistency;
- Schema extension resolution/cycles/overrides;
- forward/reverse indexes;
- derived relationships;
- semantic dependency graphs;
- bounded external-record lookup.

## What IR never owns

Canonical IR does not own:

- template selection syntax;
- renderer identities;
- generated file names/directories;
- imports/exports syntax;
- framework class names;
- project filesystem paths;
- package-manager commands;
- template-engine helper APIs.

Those belong to Packs, Planning, Render Clients, Project usage, or target templates as appropriate.
