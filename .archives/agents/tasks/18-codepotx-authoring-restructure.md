# Task 18 — Authoring compiler and engine modularization

Status: [x]
Issue: #16 closed
Depends on: Task 17 complete
Commits: implementation checkpoint from `57035ae1d56d44d90890f76b8ffcf0430f53aaaf` through `b69cb929305b15b6cc4f0987822d937d8c7eb040`; ownership and safety follow-ups through `c92a62e6f1de20d080a7ed3cbacae086469a2f2d`
Validation: combined Tasks 17–20 gate passed with 45/45 CodepotX tests, strict typechecks, structural checks, baseline artifact comparison, build, Publint, and ESM package checks.

## Goal

Split the oversized authoring compiler and engine into focused compilation passes, schema normalizers, validators, infrastructure helpers, and application use cases without changing the public DSL or compiled artifact output.

## Completed structure

```text
src/authoring/
├── compiler/{passes,schema,shared,validation}/
├── application/
├── infrastructure/
├── engine/
└── existing DSL capability folders
```

## Completion evidence

- [x] Typed compiler context owns diagnostics, indexes, and shared lookup state.
- [x] Contract collection, properties, schemas, entities, relations, access, hooks, frontends, resources, and operations are independent passes.
- [x] Zod, inline schema, ref, projection, enum, object, array, union, primitive, and schema-use normalization are separated.
- [x] Cross-operation validation preserves unique operation IDs and operation-ID-only cache invalidation.
- [x] Compile, validate, inspect, artifact load, and cache operations are focused use cases.
- [x] Source/module loading and cache infrastructure are separate from canonical compilation.
- [x] Artifact digest verification is real and centralized producer metadata is used.
- [x] `DefaultAuthoringCompiler` and `DefaultAuthoringEngine` are small facades.
- [x] Existing `codepotx` and `codepotx/authoring` imports, fluent builders, refs, generic inference, metadata, diagnostics, `.immutable()`, and `.managed()` behavior pass unchanged.
- [x] Old-style compatibility contracts and baseline authoring artifacts pass.
- [x] No explicit `any`, `@ts-ignore`, or unsafe replacement cast was introduced.

## Validation

```bash
pnpm --filter codepotx check
```
