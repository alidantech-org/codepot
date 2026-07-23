# Task 18 — Authoring compiler and engine modularization

Status: [~]
Issue: #16 open
Depends on: Task 17 strict type gate passed; combined Tasks 17-20 validation pending
Commits: implementation checkpoint from `57035ae1d56d44d90890f76b8ffcf0430f53aaaf` through `b69cb929305b15b6cc4f0987822d937d8c7eb040`; ownership and safety follow-ups through `c92a62e6f1de20d080a7ed3cbacae086469a2f2d`
Validation: compiler and engine implementations are modularized; structural, compatibility, baseline, architecture, build, and package checks are pending in the combined validation gate.

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

- [x] Introduce a typed compiler context that owns diagnostics, indexes, and shared lookup state.
- [x] Extract contract collection.
- [x] Extract property compilation.
- [x] Extract schema collection and compilation.
- [x] Extract Zod, inline schema, ref, projection, enum, object, array, union, and primitive normalization.
- [x] Extract entity compilation and lifecycle metadata.
- [x] Extract relation compilation.
- [x] Extract access compilation.
- [x] Extract hook compilation.
- [x] Extract frontend compilation.
- [x] Extract resource compilation.
- [x] Extract operation, parameter, request-body, response, effect, and cache-invalidation compilation.
- [x] Extract cross-operation and artifact validation.
- [x] Keep `DefaultAuthoringCompiler` as a small ordered orchestrator; `compiler.ts` is now a compatibility facade.

## Engine use cases

- [x] Split compile, validate, inspect, artifact loading, and cache operations into focused application modules.
- [x] Separate source/module loading infrastructure from canonical compilation.
- [x] Centralize typed success/failure result construction in `src/internal/results/operation-results.ts`.
- [x] Verify artifact body digests during artifact loading instead of carrying an unused computation.
- [x] Adopt `CODEPOT_ARTIFACT_PRODUCER` without changing serialized producer values.

## Public API and compatibility

- [ ] Confirm `codepotx` and `codepotx/authoring` exports through the full package gate.
- [x] Keep the existing public authoring barrel stable; explicit package-wide export curation remains Task 22 scope.
- [ ] Confirm fluent builder methods, refs, generic inference, metadata, errors, and validation behavior through existing fixtures.
- [ ] Confirm the real `codepotx-old` compatibility fixture under the full test suite.
- [x] Preserve accepted field lifecycle rules, including `.immutable()` and `.managed()` semantics in the entity pass.
- [x] Preserve route cache invalidation through operation IDs only; no read-cache features, scopes, tags, or string TTLs were added.

## Acceptance criteria

- [x] No authoring implementation file combines unrelated compiler passes.
- [x] The main compiler is an orchestrator and remains easy to read.
- [ ] Canonical authoring artifacts match baseline fixtures and digests.
- [ ] Public type-inference fixtures pass unchanged.
- [x] No explicit `any`, `@ts-ignore`, or new unsafe enum casts were added.
- [ ] Architecture checks show no forbidden layer imports.

## Validation

```bash
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
pnpm --filter codepotx package:lint
```
