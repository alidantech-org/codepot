# Task 18 — Authoring compiler and engine modularization

Status: [ ]
Issue: open when ready
Depends on: Task 17
Commit: pending
Validation: pending

## Goal

Split the oversized authoring compiler and authoring engine into focused compilation passes, schema normalizers, validators, and application use cases without changing the public DSL or compiled artifact output.

## Target structure

```text
src/authoring/
├── access/
├── components/
├── entities/
├── frontend/
├── hooks/
├── properties/
├── refs/
├── resources/
├── routes/
├── schemas/
├── version/
├── compiler/
│   ├── authoring-compiler.ts
│   ├── compiler-context.ts
│   ├── passes/
│   ├── schema/
│   └── validation/
├── application/
├── infrastructure/
└── index.ts
```

## Compiler passes

- [ ] Introduce a typed compiler context that owns diagnostics, indexes, and shared lookup state.
- [ ] Extract contract collection.
- [ ] Extract property compilation.
- [ ] Extract schema collection and compilation.
- [ ] Extract Zod, inline schema, ref, projection, enum, object, array, union, and primitive normalization.
- [ ] Extract entity compilation and lifecycle metadata.
- [ ] Extract relation compilation.
- [ ] Extract access compilation.
- [ ] Extract hook compilation.
- [ ] Extract frontend compilation.
- [ ] Extract resource compilation.
- [ ] Extract operation, parameter, request-body, response, effect, and cache-invalidation compilation.
- [ ] Extract cross-operation and artifact validation.
- [ ] Keep `DefaultAuthoringCompiler` as a small ordered orchestrator.

## Engine use cases

- [ ] Split compile, validate, inspect, artifact loading, and cache operations into focused application modules.
- [ ] Separate source/module loading infrastructure from canonical compilation.
- [ ] Centralize typed success/failure result construction in an approved internal result module.
- [ ] Verify artifact digest handling rather than carrying unused verification computations.
- [ ] Adopt `CODEPOT_ARTIFACT_PRODUCER` from `src/internal/package-info.ts` in canonical authoring artifact assembly without changing serialized producer values.

## Public API and compatibility

- [ ] Preserve `codepotx` and `codepotx/authoring` exports.
- [ ] Replace wildcard public barrels with explicit curated exports.
- [ ] Preserve fluent builder methods, refs, generic inference, metadata, errors, and validation behavior.
- [ ] Compare real `codepotx-old` compatibility fixtures.
- [ ] Preserve accepted field lifecycle rules, including `.immutable()` and `.managed()` semantics.
- [ ] Preserve route cache invalidation through operation IDs only; do not add read-cache features, scopes, tags, or string TTLs.

## Acceptance criteria

- [ ] No authoring implementation file combines unrelated compiler passes.
- [ ] The main compiler is an orchestrator and remains easy to read.
- [ ] Canonical authoring artifacts match baseline fixtures and digests.
- [ ] Public type-inference fixtures pass unchanged.
- [ ] No new unsafe casts or type suppressions are added.
- [ ] Architecture checks show no forbidden layer imports.

## Validation

```bash
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
pnpm --filter codepotx package:lint
```
