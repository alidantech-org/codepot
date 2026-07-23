# Codepot architecture

## Active packages

```text
packages/nodejs/
├── codepotx/
│   ├── src/
│   │   ├── contract/
│   │   ├── internal/
│   │   ├── authoring/
│   │   ├── templating/
│   │   ├── generation/
│   │   ├── platform/
│   │   ├── runtime/
│   │   └── index.ts
│   └── tests/
└── codepotx-cli/
    └── src/
```

`codepotx` and `codepotx-cli` are the active TypeScript packages. Historical Python and old Node implementations remain behavioral references only and are never imported by active source.

## Internal ownership

```text
contract/
  protocol/
  artifacts/{authoring,templating,generation}/
  operations/{authoring,templating,generation,runtime}/
  ports/{engines,infrastructure}/
  diagnostics/
  events/
  sources/

authoring/
  existing DSL domains
  compiler/{passes,schema,shared,validation}/
  application/
  infrastructure/
  engine/

templating/
  config/
  compiler/
  paths/
  context/
  references/
  variables/
  rendering/
  application/

generation/
  config/
  planning/
  rendering/
  writing/
  manifests/
  transactions/
  commands/
  caching/
  reporting/
  events/
  application/

platform/
  node/
  memory/
  shared/

runtime/
  context/
  dispatch/
  composition/
```

Folders are created only for implemented responsibilities. Generic utility warehouses and speculative empty layers are forbidden.

## Dependency direction

```text
contract   -> contract only
internal   -> internal + contract
platform   -> platform + contract + internal
authoring  -> authoring + contract + internal
templating -> templating + contract + internal
generation -> generation + contract + internal
runtime    -> contract + internal + platform + engine public APIs
CLI        -> published runtime and contract APIs
```

Generation receives `AuthoringPort` and `TemplatingPort` through explicit injection. It never imports their implementation folders. Authoring and templating never import generation. Domain modules do not call Node filesystem, child-process, Git, YAML, cache, or terminal APIs directly.

Architecture tests reject forbidden cross-layer imports, Node built-ins in domain layers, active imports from historical packages, explicit `any`, `@ts-ignore`, layer cycles, and uncurated public entrypoints.

## Contract and stable communication

`contract/` contains declarations only. It imports no authoring, templating, generation, runtime, platform, Node, Zod, Handlebars, YAML, Git, or CLI implementation.

Stable artifacts include:

- `CompiledAuthoringArtifact`
- `CompiledTemplatePack`
- `TemplateVariableCatalog`
- `GenerationPlan`
- `RenderedGeneration`
- `GenerationManifest`
- `GenerationResult`

Artifacts are versioned, readonly, deterministic, and JSON-safe. They contain no functions, Zod objects, Handlebars objects, mutable builders, platform instances, or CLI presentation state. Producer metadata is centralized under `internal/package-info.ts`.

## Authoring compiler

The authoring compiler is an ordered facade over focused passes:

```text
collect contracts
  -> compile properties
  -> compile schemas
  -> build schema lookup state
  -> compile entities and relations
  -> compile access, hooks, and frontends
  -> compile resources and operations
  -> validate operation IDs and cache invalidation
  -> assemble and digest artifact
```

Schema normalization is separate from domain passes. Projection metadata is converted through JSON-safe normalization. Field lifecycle defaults remain permissive; `.immutable()` and `.managed()` represent the supported outliers. Route cache behavior remains operation-ID invalidation only.

Compile, validate, inspect, artifact loading, and cache behavior are separate application use cases. Source/module loading and cache persistence remain infrastructure concerns.

## Templating

The templating layer compiles `paths.yaml` and template-pack files without importing authoring implementation code.

```text
parse raw YAML
  -> normalize compatibility keys
  -> validate roots and folder selections
  -> discover files
  -> classify templates, partials, and raw files
  -> compile path tokens and references
  -> validate descriptors
  -> assemble deterministic template artifact
```

Context construction consumes stable artifacts only. Variable catalog creation, formatting, strict validation, reference analysis, partial registration, and virtual-file rendering are independently testable. Handlebars prototype access and missing-helper fallbacks remain disabled.

## Generation

Generation is divided into explicit application stages:

```text
load CodepotFile
  -> prepare and validate plan inputs
  -> plan files, commands, and cleanup
  -> render virtual files
  -> write or dry-run
  -> apply manifest-owned cleanup
  -> run commands
  -> complete or roll back transaction
  -> report outcomes
```

All output paths and refusals are known before mutation. `allow: true`, dry-run behavior, managed and immutable files, protected roots, manifest cleanup, broad-clean refusal, atomic writes, cancellation, before/after command ordering, optional commands, and rollback are preserved invariants.

## Runtime

Runtime owns per-run context, typed operation dispatch, lifecycle timing, cancellation boundaries, ordered observation events, normalized failures, feature discovery, and default composition.

`RuntimeOperationMap` is the source of truth for operation request/result pairs. `RuntimeOperationHandlerRegistry` maps every operation kind to an exact handler. The registry is checked with `satisfies`; adding an operation requires a handler and does not require editing a central switch.

Runtime events are explicitly typed by event kind. Listener errors are isolated and listener return values never alter control flow.

## Platform

The platform layer implements infrastructure ports without owning domain orchestration.

### Node adapters

- filesystem and globbing;
- command execution and cancellation;
- TypeScript module loading;
- filesystem-backed cache;
- local, artifact, package, and Git source resolution.

### Memory adapters

- filesystem;
- command runner;
- module loader;
- cache;
- source registry.

### Shared capabilities

- cancellation primitives;
- YAML/JSON codec;
- sequential event bus;
- changed-aware writer;
- hashing;
- path containment and glob helpers;
- clocks and IDs;
- platform errors;
- source resolver contracts.

Default and memory composition both return the same `PlatformServices` interface. Adapter parity tests ensure shared behavior remains consistent.

## Public packages

The only supported CodepotX entrypoints are:

- `codepotx`
- `codepotx/contract`
- `codepotx/runtime`
- `codepotx/platform`
- `codepotx/authoring`
- `codepotx/templating`
- `codepotx/generation`

Every public facade uses explicit curated exports. Internal implementation folders are not package subpaths. Thin compatibility shims remain for supported repository source imports during migration, but new implementation code imports owned modules directly.

## Testing structure

```text
tests/
├── architecture/
├── compatibility/
├── contract/
├── unit/{authoring,templating,generation,runtime}/
├── integration/
└── fixtures/
```

Grouped suite entrypoints reuse the existing focused assertions. Package scripts can run each architecture area independently or execute the complete suite.

## Extension workflow

### Compiler pass

Add a typed pass under `authoring/compiler/passes/`, compose it in the compiler facade, add cross-pass validation when required, and update compatibility plus artifact baselines.

### Template capability

Normalize new `paths.yaml` syntax once, keep discovery/compilation/context/rendering separate, avoid runtime objects in artifacts, and add focused plus rendered-output tests.

### Generation stage

Add or extend the stable operation contract, implement a focused use case, depend on ports, preserve plan-before-write and rollback boundaries, and test with memory adapters.

### Runtime operation

Add the exact pair to `RuntimeOperationMap`, register the matching handler, and add inference plus dispatch coverage. Lifecycle code remains unchanged.

### Platform adapter

Implement an existing port under `node/`, `memory/`, or `shared/`, wire it through typed composition, keep business rules out, and add parity tests when multiple implementations exist.
