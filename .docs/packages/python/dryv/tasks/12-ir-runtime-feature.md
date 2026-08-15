# Task 12 — Build the IR Runtime Feature

Status: [x]
Owner: `packages/python/dryv`
Depends on: Tasks 08, 11 and canonical IR Tasks 01–07
Validation: IR load/validation/index tests, inheritance tests, derived relationship tests

> Implementation is complete on `develop`. External executable certification is still pending because the connected environment exposes no repository checkout or CI runner. See [`../PROGRESS-11-17.md`](../PROGRESS-11-17.md).

## Goal

Create `features/ir` as the runtime capability that loads, validates, resolves, indexes and inspects Canonical Dryv IR. Canonical models remain under `dryv.ir`; this Feature operates on them.

## Responsibilities

The Feature must support:

- loading canonical IR records from Serialization;
- validating contract/group ownership and semantic IDs;
- resolving typed references;
- resolving effective Schema extension chains;
- validating inheritance cycles/overrides;
- building forward and reverse semantic indexes;
- deriving relationships for template context and inspection;
- building semantic dependency graphs used by Hashing/Planning;
- bounded/lazy record lookup for JSONL-backed IR where practical;
- structured inspection/query APIs used by Runtime.

## Derived relationships

Derived indexes should include the approved directionality principle, for example:

```text
Operation emits Event
    → derive Event.emitters
Operation listens to Event
    → derive Event.listeners
Operation subject/use Schema
    → derive Schema.operations
StorageMapping maps Schema
    → derive Schema.storageMappings
View placed in Presentation
    → derive View.presentations
```

Derived information must not be written back as duplicated authored state.

## Effective Schema

Expose both:

- direct authored Schema information;
- effective resolved Schema information after its single-base extension chain is applied;
- origin/provenance of inherited fields/facts.

Planning and inspection must be able to choose the appropriate view without mutating canonical objects.

## Bounded indexes

For large JSONL IR, keep raw records separate from small hot indexes. Do not require the full serialized document and all derived contexts in memory simultaneously. Index facts should be deterministic and reloadable where disk-backed operation is implemented.

## Non-goals

- Do not select templates.
- Do not render code.
- Do not own cache persistence.
- Do not interpret project filesystem paths.

## Allowed paths

- `packages/python/dryv/src/dryv/features/ir/**`
- legacy runtime/IR validation/index modules being migrated
- corresponding tests/docs

## Acceptance criteria

- Canonical IR validation/resolution is available through one Feature facade.
- reverse relationships are derived, not authored.
- Schema extension resolves transitively with provenance.
- deterministic dependency/index queries are available for later Planning/Hashing.
- large JSONL-backed IR can be processed without a mandatory whole-document object.

## Validation

Test valid/invalid refs, duplicate IDs, inheritance chains/cycles, Event reverse indexes, Schema usage/storage indexes, Workflow/View/Presentation refs, deterministic dependency ordering and bounded JSONL lookup. Run architecture tests and `git diff --check`.
