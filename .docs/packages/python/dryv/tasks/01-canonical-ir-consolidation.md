# Task 01 — Consolidate Canonical Dryv IR ownership

Status: [ ]
Owner: `packages/python/dryv`
Depends on: Task 00
Validation: IR import-boundary tests, model tests, serialization compatibility tests

## Goal

Make `dryv.ir` the single obvious home of Canonical Dryv Runtime IR. Remove the current ambiguity where semantic models live under `dryv/domain/ir` while `dryv/ir` also exists for codec/transport concerns.

Canonical IR is the only semantic authority. All author backends target this contract, Runtime validates and indexes it, and packs consume context derived from it.

## Required outcome

Converge toward:

```text
dryv/ir/
├── kernel/
├── contract/
├── groups/
├── properties/
├── schemas/
├── policies/
├── failures/
├── events/
├── operations/
├── storage/
├── sources/
├── views/
├── workflows/
├── presentations/
└── cross_cutting/
```

The exact file granularity may stay small where a concept does not justify several files. Folder count must not become ceremony.

## Kernel responsibilities

The IR kernel should own only target-neutral primitives shared by canonical concepts, including:

- semantic identity;
- stable names;
- typed references;
- documentation metadata;
- tags;
- guidance;
- provenance/origin information;
- canonical data primitives needed for portable transport.

It must not contain generation plans, paths, template names, renderer details, filesystem state, CLI state, HTTP requests, or runtime sessions.

## Migration rules

- Move semantic model authority from `dryv/domain/ir` into `dryv/ir` incrementally.
- Preserve behavior and tests while changing import paths.
- Do not keep two independently editable model definitions during migration.
- Temporary compatibility re-exports are allowed only when they point to the new canonical definition and have a removal task/reference.
- Runtime codecs must consume canonical models rather than defining parallel transport models.
- Public imports must converge on `dryv.ir`.

## Canonical concept family to preserve

The working semantic family from the recovered authoring design must remain available for later completion:

```text
Contract
├── Groups
│   ├── Properties
│   ├── Schemas
│   ├── Policies
│   ├── Failures
│   ├── Events
│   ├── Operations
│   ├── StorageMappings
│   ├── ValueSources
│   └── Views
├── Workflows
└── Presentations
```

Cross-cutting information includes tags, guidance, documentation, provenance and typed references.

This task consolidates ownership; later tasks refine exact concept semantics.

## Non-goals

- Do not finalize pack selection vocabulary.
- Do not implement authoring APIs.
- Do not add networking.
- Do not redesign generation planning.
- Do not silently change concept ownership that remains under review.

## Allowed paths

- `packages/python/dryv/src/dryv/ir/**`
- `packages/python/dryv/src/dryv/domain/ir/**`
- compatibility imports required by the migration
- `packages/python/dryv/tests/**`
- `.docs/packages/python/dryv/**`

## Acceptance criteria

- There is one canonical Python model definition for every migrated IR concept.
- `dryv.ir` is the public semantic authority.
- Architecture tests prevent semantic models from being reintroduced outside `dryv.ir`.
- Existing supported IR round trips continue to work through the canonical definitions.
- No target/runtime/generation concepts leak into canonical models.

## Validation

Run the Dryv model/IR/codec tests, static typing checks used by the package, architecture tests from Task 00, and `git diff --check`. Record any temporary re-export remaining and the task that will remove it.
