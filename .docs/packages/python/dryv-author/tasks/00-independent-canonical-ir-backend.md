# Task 00 — Refactor `dryv-author` into an independent Canonical IR backend

Status: [ ]
Owner: `packages/python/dryv-author`
Depends on: Dryv canonical IR Tasks 01–07 and Serialization protocol contract
Validation: author compiler tests, canonical schema validation, no-engine-dependency tests

## Goal

Refactor the Python authoring package so it no longer depends on Dryv Engine internals. Its responsibility is to let Python authors describe software and compile that authored source into the versioned Canonical Dryv IR wire contract.

## Architecture

```text
Python authoring source
    ↓
dryv-author declarations/refs/compiler
    ↓
Canonical Dryv IR records
    ↓
JSON / YAML / JSONL output or Author protocol stream
```

`dryv-author` may use generated/shared protocol types or JSON Schema artifacts that describe the canonical IR contract. It must not import Runtime, Planning, Packs, Templating, Cache, Scheduling or other engine implementation modules.

## Semantic coverage

The authoring API/compiler must preserve the canonical concept family and relationships agreed in Dryv:

```text
Contract
Groups
Properties
Schemas and fields/capabilities
single-base Schema extension
Policies
Failures
Events
Operations and facets/effects
StorageMappings
ValueSources
Views
Workflows
Presentations
tags/guidance/documentation/provenance
typed refs
```

The authoring API may provide ergonomic connected authoring—for example registering related storage or operations from a Schema handle—but compilation must normalize into the independent canonical concepts rather than creating a second semantic model.

## Schema extension

Support authored:

```text
DerivedSchema extends BaseSchema
```

with zero/one direct base, nested Schema field references and explicit overrides consistent with the canonical IR contract.

## Compilation rules

- author-session refs are compiler-only and become canonical semantic IDs/refs in output;
- no process-global registry;
- deterministic IDs/order/provenance;
- wrong-kind refs fail clearly;
- unresolved forward refs follow explicit deterministic rules;
- authored reverse Event relationships are not emitted;
- no generated-code roles are promoted into canonical roots.

## Wire output

The package must be able to emit valid canonical representations:

```text
dryv.ir.json
dryv.ir.yaml
dryv.ir.jsonl
```

JSONL should support record streaming for large authoring sessions where practical.

This serialization is output of the Author Backend contract; Dryv Engine remains responsible for authoritative runtime validation/loading/indexing.

## Non-goals

- Do not generate application source code.
- Do not load/select packs.
- Do not choose output project paths.
- Do not write generated application files.
- Do not call Render Clients.
- Do not reimplement Dryv Runtime validation/indexes.

## Allowed paths

- `packages/python/dryv-author/**`
- `.docs/packages/python/dryv-author/**`
- shared/generated canonical protocol artifacts required by the backend
- root workspace metadata only where required

## Acceptance criteria

- `dryv-author` has no runtime-engine dependency.
- representative authoring can compile the full required semantic family into canonical IR.
- output validates against the canonical IR wire contract.
- JSON/YAML/JSONL output represents the same meaning deterministically.
- authoring remains cleanly separated from packs/rendering/project writes.

## Validation

Run strict typing, author compiler tests, canonical contract validation, JSON/YAML/JSONL equivalence tests, no-engine-import architecture tests and `git diff --check`.
