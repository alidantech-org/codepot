# codepotx

`codepotx` is the active TypeScript implementation of Codepot. It provides typed authoring, deterministic Handlebars template compilation, safe generation planning and execution, a typed runtime, and Node/in-memory platform adapters.

## Ownership model

Codepot combines three independently reusable inputs:

1. **Authoring source** — normally `codepotx.config.ts`, describing contracts and semantic metadata.
2. **Template pack** — Handlebars templates and `paths.yaml`, describing output structure and rendering rules.
3. **Consumer project** — `CodepotFile.yml`, selecting sources, tasks, outputs, commands, and cleanup policy.

Authoring does not prescribe framework or folder conventions. Template packs decide generated architecture. Consumer projects control when and where generation runs.

## Package entrypoints

```ts
import { defineVersionContract, defineResource, schema, z } from 'codepotx';
import type { CompiledAuthoringArtifact } from 'codepotx/contract';
import { createDefaultCodepotRuntime } from 'codepotx/runtime';
import { createMemoryPlatformServices } from 'codepotx/platform';
import { DefaultAuthoringCompiler } from 'codepotx/authoring';
import { createTemplatingEngine } from 'codepotx/templating';
import { createGenerationEngine } from 'codepotx/generation';
```

Published entrypoints are explicit and curated:

- `codepotx`
- `codepotx/contract`
- `codepotx/runtime`
- `codepotx/platform`
- `codepotx/authoring`
- `codepotx/templating`
- `codepotx/generation`

Internal folders are not supported package subpaths.

## Architecture

```text
contract
  protocol, artifacts, operations, ports, diagnostics, events, sources

internal
  package metadata, portable paths, shared operation results

authoring
  DSL domains, compiler passes, schema normalization, validation,
  application use cases, source/cache infrastructure

templating
  raw and normalized config, discovery, descriptor compilation,
  paths, references, context, variables, secure rendering

generation
  CodepotFile config, planning, rendering coordination, writing,
  manifests, transactions, commands, caching, reports, events, use cases

platform
  node adapters, memory adapters, shared infrastructure capabilities

runtime
  run context, exhaustive typed dispatch, lifecycle events, composition
```

Dependency direction is enforced by architecture tests:

```text
contract   -> contract only
internal   -> internal + contract
platform   -> platform + contract + internal
authoring  -> authoring + contract + internal
templating -> templating + contract + internal
generation -> generation + contract + internal
runtime    -> contract + platform + engine public APIs + internal
CLI        -> published runtime and contract APIs
```

Generation depends on `AuthoringPort` and `TemplatingPort`, never concrete engine implementations. Authoring and templating do not import generation. Domain layers do not call un-injected filesystem, process, Git, cache, or terminal APIs.

## Stable artifacts

The layers communicate through versioned, readonly, JSON-safe artifacts:

- `CompiledAuthoringArtifact`
- `CompiledTemplatePack`
- `TemplateVariableCatalog`
- `GenerationPlan`
- `RenderedGeneration`
- `GenerationManifest`
- `GenerationResult`

Artifacts contain no functions, Zod instances, Handlebars instances, mutable builders, CLI presentation state, or platform implementation objects. Producer metadata is centralized and artifact digests are deterministic.

## Authoring

```ts
import { defineCodepotConfig, defineVersionContract, z } from 'codepotx';

const v1 = defineVersionContract({
  info: { title: 'Example', version: '1.0.0' },
});

const schemas = v1.defineSchemas({
  User: {
    id: z.string(),
    name: z.string().min(1),
  },
});

const users = v1.defineResource({
  name: 'users',
  route: '/v1/users',
});

users.defineRoutes()
  .params(schemas.ref.User.pick({ id: true }))
  .routes((route) => ({
    listUsers: route.get('/').response(schemas.ref.User.array()),
    updateUser: route.patch('/:id')
      .body(schemas.ref.User.partial())
      .response(schemas.ref.User)
      .cache((cache) => cache.invalidate.on('listUsers')),
  }));

export default defineCodepotConfig({ contracts: [v1] });
```

Fields are selectable and editable by default. `.immutable()` permits create-time assignment but not updates. `.managed()` means the backend owns the value and implies readonly behavior. Route cache support is intentionally limited to operation-ID invalidation.

The compiler is an ordered facade over focused passes for properties, schemas, entities, relations, access, hooks, frontends, resources, operations, and cross-operation validation.

## Template packs

A template pack owns `paths.yaml`, Handlebars templates, partials, static files, selections, naming, lifecycle policy, and optional helper declarations.

Compilation is separated into:

- raw YAML input and normalized config;
- source discovery and ignore/hidden-file handling;
- partial and raw-file detection;
- folder recipes and output path tokens;
- descriptor and reference compilation;
- compiled-pack validation and digesting.

Context construction and variable introspection operate only on stable artifacts. Rendering uses a dedicated Handlebars instance with strict missing-variable behavior and prototype access disabled.

## Generation

`CodepotFile.yml` must explicitly set `allow: true` before configured generation work or commands can run.

Generation follows staged use cases:

```text
load CodepotFile
  -> resolve and validate task
  -> compile authoring and templates
  -> build and strictly validate context
  -> plan every file, command, and cleanup operation
  -> render virtual files
  -> apply managed writes and manifest cleanup
  -> run approved commands
  -> report outcomes and diagnostics
```

Complete planning happens before mutation. Dry runs do not write or execute commands. Managed, immutable, protected, refused, stale cleanup, atomic write, cancellation, command failure, and rollback behavior are explicit and tested.

## Runtime

`CodepotRuntime` accepts `RuntimeRequest<TKind>` and returns `RuntimeResponse<TKind>`. Operation request/result inference is indexed by `RuntimeOperationMap`.

The runtime uses an exhaustive mapped handler registry. Adding an operation requires a matching typed handler; lifecycle orchestration does not contain a growing switch statement. Runtime events are ordered and observational, and listener failures cannot alter required control flow.

```ts
const runtime = createDefaultCodepotRuntime({ projectRoot: process.cwd() });

const result = await runtime.execute({
  kind: 'generation.execute',
  input: { task: 'sdk' },
});
```

## Platform

`platform/node/` owns production adapters such as filesystem, command execution, TypeScript module loading, filesystem cache, and local/package/Git/artifact source resolution.

`platform/memory/` owns deterministic filesystem, command, module, cache, and source-registry adapters for tests and embedded use.

`platform/shared/` owns capabilities that are independent of one storage mode: cancellation, codec, events, changed-aware writing, hashing, portable path checks, clocks, IDs, errors, and source-resolver contracts.

Both default and memory composition satisfy the same `PlatformServices` contract.

## Extending CodepotX

### Add an authoring compiler pass

1. Add a focused file under `authoring/compiler/passes/`.
2. Give the pass an explicit typed input and output.
3. Invoke it in the intended order from `authoring-compiler.ts`.
4. Add validation in `compiler/validation/` when the rule spans passes.
5. Update authoring compatibility and artifact baseline tests.

### Add a template capability

1. Extend raw config only when `paths.yaml` needs new syntax.
2. Normalize it once in `templating/config/`.
3. Keep discovery, compilation, context, variables, references, and rendering separate.
4. Keep Handlebars runtime objects out of public artifacts.
5. Add focused unit tests plus rendered-file baseline coverage.

### Add a generation stage

1. Define or extend the stable request/result contract.
2. Add a focused use case under `generation/application/`.
3. Depend on ports, not authoring or templating implementations.
4. Preserve planning-before-write, dry-run, cancellation, and rollback invariants.
5. Add memory-adapter tests for success and failure behavior.

### Add a runtime operation

1. Add its exact request/result pair to `RuntimeOperationMap`.
2. Register a matching handler in `runtime/dispatch/create-runtime-handlers.ts`.
3. Keep lifecycle events and context handling outside the handler.
4. Add runtime inference and dispatch tests.

### Add a platform adapter

1. Implement an existing contract port under `platform/node/`, `platform/memory/`, or `platform/shared/`.
2. Wire it through a typed platform factory.
3. Do not place business orchestration or domain validation in platform code.
4. Add adapter parity tests when more than one implementation exists.

## Validation

```bash
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
pnpm --filter codepotx package:lint
```

Focused suites are also available:

```bash
pnpm --filter codepotx test:architecture
pnpm --filter codepotx test:compatibility
pnpm --filter codepotx test:contract
pnpm --filter codepotx test:unit:authoring
pnpm --filter codepotx test:unit:templating
pnpm --filter codepotx test:unit:generation
pnpm --filter codepotx test:unit:runtime
pnpm --filter codepotx test:integration
```

The package is ESM-only, targets Node.js 22.18 or newer, builds with tsdown, and validates publishability with Publint and Are The Types Wrong.

## Compatibility policy

Supported package entrypoints are stable. Thin source-level compatibility shims remain where migrated flat modules were previously imported inside the repository. New implementation code must import the owned folders, not those shims.

The preserved Python generator and `codepotx-old` remain behavioral references; active TypeScript code must not import them.
