---
title: codepot-openapi
description: The supported TypeScript-first OpenAPI contract builder and original working prototype of the Codepot project.
product: codepot-openapi
order: 10
---

# `codepot-openapi`

`codepot-openapi` is the supported TypeScript-first contract builder that began the current Codepot project.

It is a mature prototype, not an abandoned predecessor. Teams use it to define strongly typed API and software metadata, compile standard OpenAPI documents, and attach optional `x-codegen` metadata for richer generators such as [`codepotg`](/docs/codepotg).

## Install

```bash
npm install codepot-openapi zod
```

`zod` is a peer dependency.

## What it owns

- OpenAPI 3.1 version contracts;
- reusable properties and schema refs;
- schema projections such as `pick`, `omit`, and `partial`;
- resources and routes;
- parameters, request bodies, and responses;
- entity and relation metadata;
- access definitions and runtime hooks;
- frontend, screen, and component metadata;
- JSON and YAML output;
- compiler-resolved `x-codegen` metadata;
- the `codepot-openapi` CLI.

## Basic contract

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

const users = v1.defineResource({
  name: 'users',
  route: '/users',
  tags: ['users'],
});

const schemas = users.defineSchemas({
  User: {
    id: z.string().uuid(),
    email: z.string().email(),
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

Generate:

```bash
npx codepot-openapi generate
```

## OpenAPI plus Codepot metadata

The emitted document remains standard OpenAPI. Generators that understand only OpenAPI can ignore Codepot extensions.

Codepot-aware generators can additionally use metadata such as:

```text
x-codegen.resources
x-codegen.frontends
x-codegen.baseEntities
x-codegen.entities
x-codegen.access
operation.x-codegen.operation
operation.x-codegen.runtime
operation.x-codegen.parameters.target
operation.x-codegen.cache.invalidate.operations
```

Registry-backed metadata uses `$ref` pointers so repeated resource, access, hook, and relation definitions are not copied into every operation.

## Schemas and properties

`defineProperties()` creates reusable field refs. `defineSchemas()` creates reusable DTO components.

```ts
const shared = v1.defineProperties('Shared', {
  id: z.string().uuid(),
  dateTime: z.string().datetime(),
}).ref;

const base = v1.defineSchemas({
  BaseEntity: {
    id: shared.id,
    createdAt: shared.dateTime,
  },
}).ref;
```

Projection helpers preserve required and optional field behavior:

```ts
base.BaseEntity.pick({ id: true })
base.BaseEntity.omit({ createdAt: true })
base.BaseEntity.partial()
```

## Entities and relations

Entity metadata describes storage and backend meaning without silently creating public query or response schemas.

Normal fields are selectable, default-selected, creatable, and editable by default. Metadata helpers mark outliers:

```ts
readonly()
managed()
immutable()
select(false)
edit(false)
```

Relations use neutral topology metadata such as `belongsTo`, `hasOne`, `hasMany`, and `manyToMany`.

## Frontend metadata

Frontends are explicit. A resource or route does not automatically invent a screen.

Frontend components and screens reference authored operations and schemas. Their metadata is emitted under `x-codegen.frontends` for downstream generators.

## Relationship to `codepotg`

The most established workflow is:

```text
codepot-openapi contract
        ↓
OpenAPI JSON/YAML + optional x-codegen
        ↓
codepotg inference and normalized context
        ↓
Jinja template pack
        ↓
generated project code
```

Use the [Prototype workflow](/docs/prototype-workflow) guide for an end-to-end setup.

## Relationship to `codepotx`

New ideas can be validated in `codepot-openapi` and real projects, then redesigned and stabilized in `codepotx`.

`codepotx` is the official long-term JavaScript runtime rewrite, but it does not make this package unsupported today. Migration should happen only when required features and compatibility are proven.

## CLI

```bash
codepot-openapi init
codepot-openapi generate
codepot-openapi validate
```

## Development

```bash
pnpm --filter codepot-openapi typecheck
pnpm --filter codepot-openapi build
```

The package currently targets Node.js 20 or newer and publishes ESM and CommonJS entrypoints.
