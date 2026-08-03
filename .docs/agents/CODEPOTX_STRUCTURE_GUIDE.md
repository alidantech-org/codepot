# CodepotX structure migration guide

## Purpose

This guide defines the required internal folder and file structure for the active `packages/nodejs/codepotx` package. It is a non-breaking structural migration: preserve behavior, public imports, type inference, stable artifacts, diagnostics, generation safety, and package output while splitting oversized modules into focused units.

The package remains a modular monolith. Keep `codepotx` and `codepotx-cli` as the active packages; do not extract more npm packages during this migration.

## Current assessment

The top-level layers are correct:

```text
contract
runtime
platform
authoring
templating
generation
```

The scalability risk is inside those layers:

- the authoring compiler owns too many compilation concerns in one file;
- templating compilation, validation, context inspection, and rendering are combined;
- generation owns loading, planning, rendering, writing, cleanup, commands, rollback, events, and reporting in one orchestrator;
- `contract` is becoming a broad type warehouse;
- runtime dispatch grows through a central switch and unsafe casts;
- wildcard public exports expose implementation details;
- tests are flat and do not enforce architecture boundaries.

## Target package structure

```text
packages/nodejs/codepotx/
├── src/
│   ├── contract/
│   │   ├── protocol/
│   │   ├── artifacts/
│   │   │   ├── authoring/
│   │   │   ├── templating/
│   │   │   └── generation/
│   │   ├── operations/
│   │   │   ├── authoring/
│   │   │   ├── templating/
│   │   │   ├── generation/
│   │   │   └── runtime/
│   │   ├── ports/
│   │   ├── diagnostics/
│   │   ├── events/
│   │   ├── sources/
│   │   └── index.ts
│   ├── authoring/
│   │   ├── access/
│   │   ├── components/
│   │   ├── entities/
│   │   ├── frontend/
│   │   ├── hooks/
│   │   ├── properties/
│   │   ├── refs/
│   │   ├── resources/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── version/
│   │   ├── compiler/
│   │   │   ├── authoring-compiler.ts
│   │   │   ├── compiler-context.ts
│   │   │   ├── passes/
│   │   │   ├── schema/
│   │   │   └── validation/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── index.ts
│   ├── templating/
│   │   ├── config/
│   │   ├── compiler/
│   │   ├── paths/
│   │   ├── context/
│   │   ├── rendering/
│   │   ├── references/
│   │   ├── variables/
│   │   ├── application/
│   │   └── index.ts
│   ├── generation/
│   │   ├── config/
│   │   ├── planning/
│   │   ├── rendering/
│   │   ├── writing/
│   │   ├── manifests/
│   │   ├── transactions/
│   │   ├── commands/
│   │   ├── caching/
│   │   ├── reporting/
│   │   ├── events/
│   │   ├── application/
│   │   └── index.ts
│   ├── runtime/
│   │   ├── context/
│   │   ├── dispatch/
│   │   ├── composition/
│   │   ├── runtime.ts
│   │   └── index.ts
│   ├── platform/
│   │   ├── node/
│   │   ├── memory/
│   │   ├── shared/
│   │   ├── create-platform-services.ts
│   │   └── index.ts
│   ├── internal/
│   │   ├── results/
│   │   ├── paths/
│   │   ├── objects/
│   │   └── collections/
│   └── index.ts
└── tests/
    ├── unit/
    ├── integration/
    ├── compatibility/
    ├── contract/
    ├── architecture/
    └── fixtures/
```

Create only folders needed by migrated code. Do not add empty folder scaffolding.

## Dependency direction

```text
contract   -> no internal Codepot layer
internal   -> no domain layer
platform   -> contract + internal
authoring  -> contract + internal
templating -> contract + internal
generation -> contract + internal
runtime    -> contract + public engine APIs + platform
CLI        -> published codepotx runtime/contract APIs
```

Required restrictions:

- `authoring` never imports `templating`, `generation`, or platform implementations;
- `templating` never imports authoring implementation objects;
- `generation` accesses authoring and templating only through typed ports;
- `platform` contains adapters, not business orchestration;
- `internal` is small, implementation-only, and must not become a generic dumping ground;
- no domain module imports Node filesystem, child process, Git, YAML, terminal, or cache APIs directly;
- no new service locator, decorator container, global mutable registry, or reflection-based dependency injection.

## File and folder rules

### Focused files

Each implementation file should have one primary reason to change. Split a file when it combines multiple independently testable responsibilities such as loading, normalization, validation, compilation, rendering, writing, or orchestration.

A file is a refactor candidate when any of these are true:

- it implements more than one workflow stage;
- it owns several unrelated domain concepts;
- it contains a large group of private helper functions that can be named as a subsystem;
- tests cannot target its behavior without constructing the entire engine;
- a change in one feature repeatedly touches unrelated sections of the file.

Do not split tiny cohesive modules merely to satisfy a line count. As a review signal, investigate implementation files above roughly 250-350 lines, but prioritize cohesion over numeric limits.

### Folder density

Avoid placing many unrelated files directly under one folder. Group files by capability once a folder has multiple independent concepts. Examples:

- `compiler/passes/compile-operations.ts` instead of many compiler helpers in `compiler.ts`;
- `generation/manifests/` instead of manifest, stale-file, and digest logic mixed with orchestration;
- `platform/node/filesystem/` and `platform/memory/filesystem/` instead of all adapters in one flat directory.

Do not create nested folders containing only one trivial file unless the boundary is expected to grow or mirrors a stable architectural capability.

### Naming

- `*.types.ts`: interfaces, aliases, generics, and type-only declarations;
- `*.contracts.ts`: ports, requests, results, artifacts, and cross-module contracts;
- `*.constants.ts`: runtime constants;
- `*.schema.ts`: runtime validation schemas;
- normal `*.ts`: implementation;
- `index.ts`: focused public or module entrypoints only.

Use names that describe the action or capability: `compile-schemas.ts`, `plan-files.ts`, `load-codepot-file.ts`, `render-templates.ts`. Avoid broad names such as `helpers.ts`, `utils.ts`, `manager.ts`, or `service.ts` when a precise name is possible.

## Type-safety requirements

- Keep strict TypeScript settings enabled throughout the migration.
- Do not replace compiler errors with `any`, `unknown` propagation, broad assertions, `@ts-ignore`, or disabled lint/type rules.
- Remove existing `as never` dispatch casts when the typed handler registry is introduced.
- Every cross-module function has an explicit input and output contract.
- Preserve generic inference in the public authoring DSL.
- Stable artifacts remain deterministic, immutable, JSON-serializable, and versioned.
- No Zod or Handlebars instance may leak into stable artifacts or public contract types.
- Prefer discriminated unions and exhaustive checks for operation dispatch and artifact kinds.
- Add compile-time type fixtures for public API inference and intentional type errors.

## Public API rules

- Preserve existing package subpath exports during the migration.
- Replace wildcard public barrels with explicit curated exports.
- Internal files are not public merely because they have an `index.ts`.
- Add export-surface tests before moving implementations.
- Do not introduce deep public imports into documentation or tests.
- Package output must continue to pass TypeScript declaration checks, Publint, and Are The Types Wrong.

## Migration invariants

Every structural change must preserve:

- public import paths and exported symbol meaning;
- fluent builder behavior and generic inference;
- authoring compatibility fixtures;
- artifact field names and serialized meaning unless a separately approved protocol migration exists;
- template path, context, variable, reference, partial, and rendering behavior;
- deterministic planning and content digests;
- managed, immutable, protected, cleanup, transaction, and rollback behavior;
- command ordering, dry-run behavior, cancellation, events, diagnostics, and reports;
- Node and in-memory adapter behavior;
- CLI behavior through the external `codepotx-cli` package.

Move code before redesigning behavior. A discovered bug must be recorded and fixed as a separate reviewable change rather than hidden inside a structural move.

## Migration method

1. Capture a clean baseline: typecheck, tests, build, package lint, export surface, artifact snapshots, and representative generated output.
2. Add architecture tests before moving implementation.
3. Move one capability at a time without changing behavior.
4. Keep compatibility re-export shims only when necessary and remove them in a later explicit cleanup task.
5. Validate after each independently reviewable chunk.
6. Commit each completed compiler pass, subsystem, or boundary migration separately.
7. Update task evidence with commands, test counts, commit SHA, and issue closure.

Do not perform a repository-wide file move followed by one large repair commit.

## Required architecture tests

Add automated checks for:

- forbidden cross-layer imports;
- Node built-in imports outside approved platform/runtime infrastructure;
- public export snapshots;
- JSON serialization of stable artifacts;
- deterministic artifact and generation output;
- absence of circular dependency paths across public module entrypoints;
- package subpath importability;
- no accidental imports from `codepotx-old` or `codepotg` runtime code.

## Validation gates

Run the focused package checks after each migration chunk:

```bash
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
pnpm --filter codepotx package:lint
```

Before completing the migration, also run workspace checks and the external CLI tests:

```bash
pnpm check
pnpm --filter codepotx-cli check
```

Validation must include representative authoring compilation, template compilation, generation planning, dry-run generation, real managed writing in a temporary workspace, rollback behavior, and package-consumer imports.

## Non-goals

This migration does not:

- split CodepotX into many npm packages;
- redesign the authoring DSL;
- change artifact protocol meaning;
- add new product features;
- replace Handlebars, Zod, tsdown, pnpm, or Turbo;
- modify the Python `codepotg` package;
- remove `codepotx-old` until compatibility work no longer needs it.

## Completion definition

The structure migration is complete only when:

- all migration tasks are complete and issues closed;
- oversized multi-responsibility engines delegate to focused modules;
- dependency boundaries are enforced automatically;
- public exports are explicit and validated;
- tests mirror the source architecture;
- strict typecheck, tests, build, package lint, CLI checks, and workspace checks pass;
- representative artifacts and generated files match the recorded baseline;
- documentation reflects the implemented structure.
