# Task 02 — Complete Contract, Group, and Property semantics

Status: [ ]
Owner: `packages/python/dryv`
Depends on: Task 01
Validation: semantic model tests, reference-resolution tests, architecture tests

## Goal

Complete the outer canonical semantic structure without introducing generated-code vocabulary.

Working model:

```text
Contract
├── Groups
├── Workflows
└── Presentations

Group
├── Properties
├── Schemas
├── Policies
├── Failures
├── Events
├── Operations
├── StorageMappings
├── ValueSources
└── Views
```

The exact Presentation ownership is still reviewable; implementation must preserve the current approved/partially approved shape without silently relocating it.

## Contract

`Contract` is the complete canonical semantic package produced by an author backend and consumed by Runtime.

It must provide:

- stable contract identity/version facts required by the IR contract;
- deterministic collections of owned semantic roots;
- documentation, tags, guidance and provenance where applicable;
- no pack configuration, template configuration, output paths or build state.

## Group

`Group` is a semantic domain/module boundary used to organize connected meaning. It is not inherently a filesystem folder, namespace, package, service or deployment unit.

Support explicit ownership of the Group-level roots listed above and prepare for later boundary facts such as public/internal exposure and permitted cross-Group dependencies without inventing implementation-specific module concepts.

Cross-Group references must remain typed and explicit. Runtime must be able to validate ownership and resolve references deterministically.

## Property

`Property` is reusable semantic value meaning that schemas may reference instead of duplicating primitive constraints.

It may carry:

- canonical type expression;
- format;
- constraints;
- documentation;
- tags/guidance;
- provenance.

Examples of meaning include Email, Money, Identifier, Slug, Timestamp and PhoneNumber, but no specific standard-library catalog is required in this task.

## Determinism

- Canonical collection ordering must be deterministic.
- Duplicate semantic IDs must be rejected.
- Ownership must be unambiguous.
- References must not depend on Python object identity or process-global registries.

## Non-goals

- Do not define package/template selection syntax.
- Do not make Group equal to package/module/service.
- Do not implement filesystem paths.
- Do not finalize public/internal Group dependency rules unless already represented by an approved contract; leave extension points typed and minimal.
- Do not build authoring helpers.

## Allowed paths

- `packages/python/dryv/src/dryv/ir/contract/**`
- `packages/python/dryv/src/dryv/ir/groups/**`
- `packages/python/dryv/src/dryv/ir/properties/**`
- shared IR kernel/reference files required by these concepts
- corresponding tests and canonical Dryv docs

## Acceptance criteria

- Contract, Group and Property have one canonical definition under `dryv.ir`.
- Group ownership is explicit and deterministic.
- Properties are reusable through typed refs rather than copied dictionary blobs.
- No generation or target-specific concepts enter the models.
- Invalid duplicate ownership/reference cases fail clearly.

## Validation

Add focused tests for valid ownership, duplicate IDs, cross-Group references, deterministic ordering and Property reuse. Run package tests, architecture tests and `git diff --check`.
