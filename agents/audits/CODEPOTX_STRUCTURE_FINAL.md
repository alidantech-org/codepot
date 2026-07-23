# CodepotX final structure audit

Date: 2026-07-23
Branch: `chatgpt/codepotx-restart`
Program: Tasks 15–23
Issues: #14–#21

## Executive result

The CodepotX package remains one modular-monolith npm package with a separate thin CLI. The migration did not split domain layers into additional packages. Instead, it introduced enforceable internal ownership, typed stable boundaries, explicit public entrypoints, grouped tests, and compatibility shims for supported repository source imports.

Implemented layers:

```text
contract
internal
authoring
templating
generation
platform
runtime
```

The active package does not import historical Python or old Node implementations.

## Contract ownership

`contract/` owns declarations only:

- protocol versions and artifact headers;
- authoring, templating, and generation artifacts;
- operation requests and results;
- engine and infrastructure ports;
- diagnostics and operation results;
- events;
- source descriptors.

Contract imports are type-focused and contain no Node, Zod, Handlebars, YAML, Git, platform, domain implementation, runtime implementation, or CLI dependency.

## Authoring ownership

The public DSL remains organized by access, components, config, core, entities, frontend, hooks, properties, refs, resources, routes, schema, and version.

Compiler ownership:

```text
compiler/
├── authoring-compiler.ts
├── compiler-context.ts
├── passes/
├── schema/
├── shared/
└── validation/
```

The compiler facade orders focused passes. Application use cases own compile, validate, inspect, artifact load, and cache operations. Infrastructure owns source/module resolution and cache persistence.

Preserved behavior:

- fluent builder and ref inference;
- projection and extension chains;
- JSON-safe deterministic artifacts;
- `.immutable()` and `.managed()` field lifecycle rules;
- route cache invalidation by operation ID only;
- old-style import-only compatibility.

## Templating ownership

```text
templating/
├── config/
├── compiler/
├── paths/
├── context/
├── references/
├── variables/
├── rendering/
└── application/
```

Raw `paths.yaml` input and normalized config are separate. Discovery, descriptor compilation, references, validation, artifact assembly, context, variable introspection, and secure rendering are independently owned.

Preserved behavior:

- camelCase and accepted snake_case config keys;
- hidden, ignored, partial, raw, and static files;
- folder selections and aliases;
- embedded output expressions and portable paths;
- strict Handlebars security;
- deterministic descriptors, contexts, catalogs, files, and digests.

## Generation ownership

```text
generation/
├── config/
├── planning/
├── rendering/
├── writing/
├── manifests/
├── transactions/
├── commands/
├── caching/
├── reporting/
├── events/
└── application/
```

Application use cases:

- load CodepotFile;
- plan generation;
- render generation;
- write generation;
- clean generation;
- run generation commands;
- execute generation.

Preserved safety:

- explicit `allow: true`;
- complete planning before mutation;
- dry-run without writes or commands;
- managed, immutable, protected, and refused files;
- manifest-owned stale cleanup;
- broad-clean refusal;
- atomic writes and rollback;
- required and optional command behavior;
- cancellation between stages;
- deterministic plans, manifests, reports, and cache keys.

## Runtime ownership

```text
runtime/
├── context/
├── dispatch/
├── composition/
├── runtime-event-publisher.ts
└── runtime.ts
```

`RuntimeOperationMap` indexes exact request/result pairs. `RuntimeOperationHandlerRegistry` is an exhaustive mapped type, and handler registration uses `satisfies`. Runtime lifecycle code contains no growing operation switch and no `as never` dispatch chain.

Runtime owns:

- per-run context;
- cancellation boundaries;
- typed dispatch;
- lifecycle timing;
- ordered typed observation events;
- failure normalization;
- feature discovery;
- default composition.

## Platform ownership

```text
platform/
├── node/
├── memory/
└── shared/
```

Node adapters:

- filesystem;
- command runner;
- TypeScript module loader;
- filesystem cache;
- local, artifact, package, and Git source resolver.

Memory adapters:

- filesystem;
- command runner;
- module loader;
- cache;
- source store.

Shared capabilities:

- cancellation;
- YAML/JSON codec;
- event bus;
- changed-aware writer;
- hashing;
- portable path and glob utilities;
- clocks and IDs;
- platform errors;
- source resolver contracts.

Default and memory composition satisfy the same `PlatformServices` contract.

## Public package boundary

Published entrypoints remain unchanged:

- `codepotx`
- `codepotx/contract`
- `codepotx/runtime`
- `codepotx/platform`
- `codepotx/authoring`
- `codepotx/templating`
- `codepotx/generation`
- package metadata JSON

Every TypeScript entrypoint uses explicit curated exports. Compiler passes, use-case internals, runtime handler internals, and platform capability implementation paths are not package subpaths.

Public consumer fixtures compile against every entrypoint. Runtime value snapshots reject accidental additions or removals.

## Compatibility shims

Thin compatibility files remain for supported repository source imports after implementation ownership moved. Examples include:

- flat contract type files;
- `authoring/compiler/compiler.ts`;
- `runtime/run-context.ts` and `runtime/default-runtime.ts`;
- moved flat platform files such as cache, command runner, codec, event bus, writer, hash, filesystem, module loader, source resolver, cancellation, errors, paths, and system.

Rules:

1. a shim re-exports only the owned implementation;
2. a shim contains no orchestration or duplicate logic;
3. new implementation code imports owned folders directly;
4. shims may be removed only after supported consumers prove they are unnecessary.

## Test ownership

```text
tests/
├── architecture/
├── compatibility/
├── contract/
├── unit/{authoring,templating,generation,runtime,platform}/
├── integration/
└── fixtures/
```

The complete runner imports grouped entrypoints. Independent scripts run every major architecture area. Existing assertions are reused exactly once.

Guardrails cover:

- dependency direction and cycles;
- forbidden Node imports in domain layers;
- historical implementation imports;
- explicit `any` and `@ts-ignore`;
- contract ownership;
- public package export keys;
- public runtime value surfaces;
- wildcard public exports;
- compiler/engine facade size;
- exhaustive runtime handlers;
- platform ownership and compatibility-shim size;
- deterministic artifacts and generation behavior;
- adapter parity;
- CLI thinness.

## Validation history

Task 16 baseline gate passed:

- 40 CodepotX tests;
- 3 CLI tests;
- strict typechecks;
- builds;
- Publint;
- ESM package resolution.

Combined Tasks 17–20 gate passed:

- 45 CodepotX tests;
- 3 CLI tests;
- strict source and test typechecks;
- architecture and compatibility checks;
- deterministic artifact and generation tests;
- package builds;
- Publint;
- ESM package resolution.

## Final gate

Tasks 21–23 require one final combined execution after all commits:

```bash
pnpm --filter codepotx check
pnpm --filter codepotx-cli check
pnpm check
pnpm build
```

Completion requires:

- all strict typechecks pass;
- every grouped and complete test passes;
- CodepotX and CLI builds pass;
- workspace checks and build pass;
- Publint and Are The Types Wrong pass;
- no public export drift or private declaration path appears;
- issues #19, #20, and #21 close;
- Tasks 15, 21, 22, and 23 become complete.
