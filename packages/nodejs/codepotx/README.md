# codepotx

`codepotx` is the official JavaScript runtime rewrite and long-term-supported release line for Codepot.

It stabilizes ideas proven in `codepot-openapi` and `codepotg` behind explicit package boundaries, versioned JSON-safe artifacts, deterministic planning, safe generation, platform adapters, and a frontend-neutral runtime. The current package is under active development and has not yet reached its first stable npm release.

## Role in the ecosystem

```text
codepot-openapi + codepotg
        ↓ prove contract and generation behavior in real projects
codepotx
        ↓ stabilize typed artifacts and runtime operations
Codepot Lang + final Codepot platform
```

The supported prototype packages continue to complement `codepotx`. They are not treated as abandoned simply because the rewrite exists.

## Frontend-neutral runtime

`codepotx` is not just a CLI implementation. Its runtime can be driven by:

- `codepotx-cli`;
- programmatic Node.js applications;
- editor extensions;
- web or desktop interfaces;
- MCP servers and AI integrations;
- test and in-memory harnesses.

The CLI remains a thin frontend so every client shares the same authoring, planning, safety, diagnostics, and execution behavior.

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

Supported exports:

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
  versioned protocols, artifacts, operations, ports, diagnostics, events, sources

internal
  package metadata, portable paths, shared operation results

authoring
  typed DSL domains, compiler passes, normalization, validation, source loading

templating
  paths.yaml, discovery, descriptors, references, variables, secure Handlebars rendering

generation
  CodepotFile.yml, planning, rendering, manifests, transactions, commands, reports

platform
  Node adapters, memory adapters, cancellation, codecs, hashing, events, source resolution

runtime
  typed requests, exhaustive dispatch, lifecycle events, composition
```

Architecture tests enforce dependency direction. Generation depends on authoring and templating ports rather than concrete engine implementations. Domain layers do not reach directly into filesystem, process, Git, cache, or terminal APIs.

## Stable artifacts

The major layers communicate through readonly, deterministic, JSON-safe artifacts such as:

- `CompiledAuthoringArtifact`
- `CompiledTemplatePack`
- `TemplateVariableCatalog`
- `GenerationPlan`
- `RenderedGeneration`
- `GenerationManifest`
- `GenerationResult`

Artifacts do not contain Zod instances, Handlebars instances, mutable builders, CLI presentation state, or platform implementation objects.

## Authoring

```ts
import { defineCodepotConfig, defineVersionContract, z } from 'codepotx';

const v1 = defineVersionContract({
  info: { title: 'Example', version: '1.0.0' },
});

const schemas = v1.defineSchemas({
  User: {
    id: z.string().uuid(),
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

Fields are selectable and editable by default. `.immutable()` permits create-time assignment but blocks updates. `.managed()` marks backend-owned readonly values. Cache metadata is intentionally limited to operation-ID invalidation in the current contract.

## Template packs

A template pack owns generated architecture through:

- `paths.yaml`;
- Handlebars templates and partials;
- selectors and aliases;
- output path tokens;
- raw and static files;
- variables and requirements;
- managed and immutable lifecycle rules.

Rendering uses strict missing-variable behavior with prototype access disabled. Context and variable inspection operate only on stable artifacts.

## Generation

`CodepotFile.yml` binds authoring, templates, output, commands, cleanup scopes, and project variables. It must explicitly include `allow: true` before generation or configured commands can run.

```text
load CodepotFile.yml
  -> resolve task and sources
  -> compile authoring and template artifacts
  -> validate context and variables
  -> plan every output, command, and cleanup action
  -> render virtual files in memory
  -> apply managed writes and manifest cleanup
  -> run approved commands
  -> return reports and diagnostics
```

Dry runs do not write files or execute commands. Managed, immutable, protected, refused, stale-cleanup, cancellation, command-failure, and rollback behavior are explicit and tested.

## Runtime

```ts
import { createDefaultCodepotRuntime } from 'codepotx/runtime';

const runtime = createDefaultCodepotRuntime({
  projectRoot: process.cwd(),
});

const response = await runtime.execute({
  kind: 'generation.execute',
  input: { task: 'sdk' },
});
```

Runtime request/result inference is indexed by `RuntimeOperationMap`. Adding an operation requires a matching typed handler. Lifecycle events are observational, and listener failures cannot alter required control flow.

## Platform adapters

- `platform/node` owns production filesystem, command, TypeScript module, cache, and source-resolution adapters.
- `platform/memory` owns deterministic adapters for tests and embedded use.
- `platform/shared` owns storage-independent capabilities such as cancellation, hashing, codecs, changed-aware writing, events, paths, clocks, IDs, and errors.

Both compositions satisfy the same `PlatformServices` contract.

## Validation

```bash
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
pnpm --filter codepotx package:lint
```

Focused suites include architecture, compatibility, contract, authoring, templating, generation, runtime, platform, and integration tests.

The package is ESM-only, targets Node.js 22.18 or newer, and validates publishability with Publint and Are The Types Wrong.

## Compatibility policy

Published entrypoints are the supported boundary. Compatibility shims may remain inside the implementation while code is migrated, but new work should import the owned public modules. Active implementation must not depend on stale historical packages.

## License

MIT
