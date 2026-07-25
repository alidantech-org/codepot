# codepot-openapi

`codepot-openapi` is the supported TypeScript-first prototype that started the wider Codepot project. It lets teams author typed API and software contracts, compile them to OpenAPI 3.1 JSON or YAML, and preserve generator-focused semantics through resolved `x-codegen` metadata.

The package remains active and useful in real projects. It is not an abandoned predecessor to `codepotx`: it is the mature contract-authoring side of the current prototype workflow and a proving ground for ideas that can later be stabilized in the official runtime.

## Install

```bash
npm install codepot-openapi zod
```

`zod` is a peer dependency.

- npm: https://www.npmjs.com/package/codepot-openapi
- source: https://github.com/alidantech-org/codepot/tree/main/packages/nodejs/codepot-openapi
- ecosystem documentation: https://github.com/alidantech-org/codepot/tree/main/docs/packages/codepot-openapi.md

## What it provides

- typed OpenAPI 3.1 contract authoring;
- reusable properties and schema refs backed by Zod;
- projections through `pick`, `omit`, `partial`, arrays, optional, and nullable usage;
- version contracts, resources, operations, parameters, request bodies, and responses;
- entity, relation, constraint, access, hook, frontend, UI, and implementation-information metadata;
- deterministic JSON and YAML output;
- validation of refs, routes, metadata registries, and cache invalidation targets;
- a CLI and programmatic compiler API.

## Minimal example

```ts
import {
  ContentType,
  definePackageConfig,
  defineVersionContract,
} from 'codepot-openapi';
import { z } from 'zod';

const v1 = defineVersionContract({
  info: {
    title: 'Example API',
    version: 'v1',
  },
  defaults: {
    requestContentType: ContentType.json,
    responseContentType: ContentType.json,
  },
});

const shared = v1.defineProperties('Shared', {
  id: z.string().uuid(),
  email: z.string().email(),
}).ref;

const users = v1.defineResource({
  name: 'users',
  route: '/users',
});

const schemas = users.defineSchemas({
  User: {
    id: shared.id,
    email: shared.email,
  },
}).ref;

users.defineRoutes().routes((route) => ({
  listUsers: route.get('/').response(schemas.User.array()),
  getUser: route.get('/:id').response(schemas.User),
}));

export default definePackageConfig({
  contracts: [v1],
  output: {
    folder: 'openapi',
    filePrefix: 'openapi',
    formats: ['json', 'yaml'],
  },
});
```

Generate files:

```bash
codepot-openapi generate
```

## Relationship to codepotg

The supported prototype workflow is:

```text
TypeScript contracts in codepot-openapi
                ↓
OpenAPI JSON/YAML + optional x-codegen metadata
                ↓
codepotg normalized inference + Jinja template packs
                ↓
generated project files
```

Standard OpenAPI remains usable on its own. `x-codegen` enriches generators with Codepot-specific resource placement, entity semantics, access rules, frontends, screens, hooks, UI roles, and documentation guidance.

## Relationship to codepotx

`codepotx` is the official JavaScript runtime rewrite. Features can be explored and proven in `codepot-openapi` and `codepotg`, then redesigned behind stable typed artifacts and runtime operations in `codepotx`.

The packages currently complement one another. A future migration or replacement decision will happen only after `codepotx` is stable and feature-complete enough for affected projects.

## CLI

```bash
codepot-openapi init
codepot-openapi generate
codepot-openapi validate
```

## Programmatic API

```ts
import {
  OpenApiTs,
  compileOpenApi,
  generateOpenApi,
  validateOpenApiDocument,
} from 'codepot-openapi';
```

## Development

```bash
pnpm install
pnpm typecheck
pnpm build
pnpm pack:dry
```

The package targets Node.js 20 or newer and publishes ESM, CommonJS, and TypeScript declarations.

## License

MIT
