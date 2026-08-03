---
title: Getting started with codepot-openapi
description: Install the package, author a first contract, and generate OpenAPI files.
product: codepot-openapi
package: codepot-openapi
order: 2
---

# Getting started

## Requirements

- Node.js 20 or newer
- TypeScript
- Zod 4

Install the package and its peer dependency:

```bash
npm install codepot-openapi zod
```

## Create a contract file

Create `codepot-openapi.config.ts` in the project root:

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
    version: '1.0.0',
    description: 'Example contract generated from typed TypeScript.',
  },
  defaults: {
    requestContentType: ContentType.json,
    responseContentType: ContentType.json,
  },
});

const shared = v1.defineProperties('Shared', {
  id: z.string().uuid(),
  createdAt: z.string().datetime(),
}).ref;

const users = v1.defineResource({
  name: 'users',
  route: '/users',
});

const schemas = users.defineSchemas({
  User: {
    id: shared.id,
    name: z.string().min(1),
    email: z.string().email(),
    createdAt: shared.createdAt,
  },
  CreateUser: {
    name: z.string().min(1),
    email: z.string().email(),
  },
}).ref;

users.defineRoutes().routes((route) => ({
  listUsers: route.get('/').response(schemas.User.array()),
  getUser: route.get('/:id').response(schemas.User),
  createUser: route.post('/').body(schemas.CreateUser).response(schemas.User),
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

## Generate files

```bash
npx codepot-openapi generate
```

The configured output folder receives deterministic OpenAPI files for each version contract.

## Validate without changing contracts

```bash
npx codepot-openapi validate
```

Validation checks the authored contract and the emitted OpenAPI document. Package configuration can decide whether warnings fail the command and whether unused components are accepted.

## Initialize a project

```bash
npx codepot-openapi init
```

The initialization command creates a starter configuration. Review the generated contract instead of treating it as application-specific design.

## Programmatic generation

```ts
import { generateOpenApi } from 'codepot-openapi';
import config from './codepot-openapi.config.js';

const result = await generateOpenApi({
  config,
  cwd: process.cwd(),
});
```

Use the CLI for ordinary project workflows and the programmatic API when generation is embedded in another Node.js tool.

## Next steps

- [Architecture](/docs/packages/codepot-openapi/architecture)
- [Schemas and refs](/docs/packages/codepot-openapi/schemas)
- [Resources and routes](/docs/packages/codepot-openapi/resources-routes)
- [Generation and validation](/docs/packages/codepot-openapi/generation-validation)