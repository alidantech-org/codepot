# Codepot architecture

## Target package shape

```text
packages/nodejs/
├── codepotx/
│   └── src/
│       ├── contract/
│       ├── runtime/
│       ├── authoring/
│       ├── templating/
│       ├── generation/
│       ├── platform/
│       └── index.ts
└── codepotx-cli/
    └── src/
```

Subfolders are added only when a module becomes large enough to justify them. The intended internal shape is:

```text
contract/    artifacts, ports, requests, events, diagnostics
runtime/     composition root, run context, service wiring, event bus
platform/    Node and in-memory adapters for shared infrastructure ports
authoring/   public DSL, model, compiler, validation, compatibility
templating/  paths, context, rendering, dependency/import planning
generation/  CodepotFile config, planning, execution, writing
```

## Dependency direction

```text
contract   -> nothing
platform   -> contract
authoring  -> contract
templating -> contract
generation -> contract
runtime    -> contract + platform + engine implementations
CLI        -> contract + runtime
```

Generation receives `AuthoringPort` and `TemplatingPort` through constructor/factory injection. It must never import their concrete internals. Authoring and templating never import generation.

## Stable communication artifacts

- `CompiledAuthoringArtifact` is the deterministic, versioned, JSON-serializable result of user authoring.
- `CompiledTemplatePack` is the deterministic result of `paths.yaml`, template, static-file, selection, dependency, and lifecycle validation.
- `GenerationPlan` is an immutable plan created before rendering or writing.
- `RenderedGeneration` contains virtual files in memory.
- `GenerationResult` records writes, skips, immutable behavior, refusals, cleanup, commands, and diagnostics.

Artifacts contain no functions, Zod instances, Handlebars instances, mutable builders, CLI presentation state, or machine-specific implementation objects.

## Runtime and dependency injection

Runtime is the composition root. Default construction uses explicit typed factories:

```ts
const runtime = createCodepotRuntime({
  services: createDefaultRuntimeServices(),
  authoring: createAuthoringEngine(...),
  templating: createTemplatingEngine(...),
  generation: createGenerationEngine(...),
});
```

Use constructor/factory injection rather than decorators, reflection metadata, or a generic service locator. Tests can inject memory filesystems, disabled command runners, deterministic clocks, fixed IDs, and event collectors.

## Shared platform ports

The contract defines narrow ports for:

- filesystem reads, writes, listing, globbing, stats, removal, and real paths;
- changed-aware and atomic file writing;
- YAML and JSON codecs;
- TypeScript module loading;
- local, package, Git, and artifact source resolution;
- hashing and source-graph fingerprints;
- caching;
- command execution;
- clock and ID generation;
- runtime events.

Domain modules do not call Node filesystem, child-process, Git, YAML, or cache APIs directly.

## Event model

Typed events are for observation only: progress, diagnostics, tracing, file lifecycle, command lifecycle, and frontend updates. Core orchestration uses explicit port calls and returned results.

Every event carries a version, ID, run ID, sequence, timestamp, source module, type, and payload. Listener errors are isolated and observer return values are ignored.

## Authoring compilation

`codepotx.config.ts` is loaded with the consumer's TypeScript configuration. Only the reachable import graph is executed. Existing builders are validated and normalized directly into `CompiledAuthoringArtifact`; OpenAPI is not required between authoring and generation.

The old authoring API is ported before it is refactored. Compatibility is validated against real old contracts and old compiler behavior.

## Generation flow

```text
frontend request
  -> runtime
  -> generation loads CodepotFile.yml
  -> authoring port resolves and compiles source
  -> templating port resolves and compiles template pack
  -> generation plans files
  -> templating renders virtual files
  -> generation writer commits allowed changes
  -> generation runs approved commands
  -> runtime returns result and events
```
