# codepotx

`codepotx` is the official JavaScript runtime rewrite and long-term release line for Codepot.

It stabilizes ideas proven in `codepot-openapi` and `codepotg` behind explicit package boundaries, versioned JSON-safe artifacts, deterministic planning, safe generation, platform adapters, and a frontend-neutral runtime.

The current package version is `0.0.0` and is under active workspace development. It has not yet reached its first stable npm release.

- documentation: https://code.alidantech.org/docs/packages/codepotx
- source: https://github.com/alidantech-org/codepot/tree/main/packages/nodejs/codepotx

The complete documentation covers getting started, architecture, typed authoring, Handlebars template packs, generation, stable artifacts, runtime operations, platform adapters, best practices, and troubleshooting.

## Role in the ecosystem

```text
codepot-openapi + codepotg
        ↓ prove contract and generation behavior in real projects
codepotx
        ↓ stabilize typed artifacts and runtime operations
Codepot Lang + final Codepot platform
```

The supported prototype packages continue to complement `codepotx`. They are not abandoned merely because the rewrite exists.

## Frontend-neutral runtime

The runtime can be driven by:

- `codepotx-cli`;
- programmatic Node.js applications;
- editor extensions;
- web or desktop interfaces;
- MCP servers and AI integrations;
- test and in-memory harnesses.

The CLI remains a thin frontend so every client shares the same authoring, planning, safety, diagnostics, and execution behavior.

## Supported entrypoints

```ts
import { defineVersionContract, defineResource, schema, z } from 'codepotx';
import type { CompiledAuthoringArtifact } from 'codepotx/contract';
import { createDefaultCodepotRuntime } from 'codepotx/runtime';
import { createMemoryPlatformServices } from 'codepotx/platform';
import { DefaultAuthoringCompiler } from 'codepotx/authoring';
import { createTemplatingEngine } from 'codepotx/templating';
import { createGenerationEngine } from 'codepotx/generation';
```

Published package boundaries are:

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

authoring
  typed DSL domains, compiler passes, normalization, validation, source loading

templating
  paths.yaml, discovery, descriptors, variables, secure Handlebars rendering

generation
  CodepotFile.yml, planning, rendering, manifests, transactions, commands, reports

platform
  Node and memory adapters, cancellation, codecs, hashing, events, source resolution

runtime
  typed requests, exhaustive dispatch, lifecycle events, composition
```

Architecture tests enforce dependency direction. Domain layers do not reach directly into filesystem, process, Git, cache, or terminal APIs.

## Stable artifacts

Major layers communicate through readonly, deterministic, JSON-safe artifacts such as:

- `CompiledAuthoringArtifact`
- `CompiledTemplatePack`
- `TemplateVariableCatalog`
- `GenerationPlan`
- `RenderedGeneration`
- `GenerationManifest`
- `GenerationResult`

Artifacts do not contain Zod instances, Handlebars instances, mutable builders, CLI presentation state, or platform implementation objects.

## Runtime example

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

`CodepotFile.yml` must explicitly include `allow: true` before generation or configured commands can run. Dry runs do not write files or execute commands.

## Validation

```bash
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
pnpm --filter codepotx package:lint
```

Focused suites cover architecture, compatibility, contract, authoring, templating, generation, runtime, platform, and integration behavior.

The package is ESM-only and targets Node.js 22.18 or newer.

## Compatibility policy

Published entrypoints are the supported boundary. Compatibility shims may remain inside the implementation while code is migrated, but new work should import the owned public modules. Active implementation must not depend on stale historical packages.

## License

MIT
