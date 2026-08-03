---
title: Getting started with codepotx
description: Build, validate, and evaluate the active workspace runtime before its first stable release.
product: codepotx
package: codepotx
order: 2
---

# Getting started

`codepotx` is currently consumed from the repository workspace.

## Requirements

- Node.js 22.18 or newer
- Corepack and pnpm

From the repository root:

```bash
corepack enable
pnpm install
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
```

Run the complete package check:

```bash
pnpm --filter codepotx check
```

## Author a contract

Create `codepotx.config.ts`:

```ts
import {
  defineCodepotConfig,
  defineVersionContract,
  z,
} from 'codepotx';

const v1 = defineVersionContract({
  info: {
    title: 'Example API',
    version: '1.0.0',
  },
});

const schemas = v1.defineSchemas({
  User: {
    id: z.string().uuid(),
    name: z.string().min(1),
  },
});

const users = v1.defineResource({
  name: 'users',
  route: '/users',
});

users
  .defineRoutes()
  .params(schemas.ref.User.pick({ id: true }))
  .routes((route) => ({
    listUsers: route.get('/').response(schemas.ref.User.array()),
    updateUser: route
      .patch('/:id')
      .body(schemas.ref.User.partial())
      .response(schemas.ref.User)
      .cache((cache) => cache.invalidate.on('listUsers')),
  }));

export default defineCodepotConfig({
  contracts: [v1],
});
```

## Add a template pack

A pack contains `paths.yaml`, Handlebars templates, and optional partials or raw files.

```text
templates/typescript/
├── paths.yaml
├── models/
│   └── model.ts.hbs
└── partials/
```

## Add `CodepotFile.yml`

```yaml
allow: true

tasks:
  sdk:
    authoring:
      source: ./codepotx.config.ts
    templates:
      source: ./templates/typescript
    output: ./generated/sdk
```

The exact source shape is validated by the active package contracts. Keep project files aligned with the workspace version being evaluated.

## Use the runtime

```ts
import { createDefaultCodepotRuntime } from 'codepotx/runtime';

const runtime = createDefaultCodepotRuntime({
  projectRoot: process.cwd(),
});

const response = await runtime.execute({
  kind: 'generation.plan',
  input: { task: 'sdk' },
});
```

Use runtime operations instead of calling internal compiler or filesystem implementations directly.

## Use the CLI

The companion `codepotx-cli` package exposes the `codepotx` binary from the workspace.

```bash
codepotx validate
codepotx variables sdk
codepotx plan sdk --json
codepotx generate sdk --dry-run
```

## Release-status guidance

- Do not add a public npm install command until the package is actually released.
- Pin the workspace commit when evaluating it in another repository.
- Expect public artifacts and entrypoints to be the compatibility boundary.
- Read migration notes before moving a production project away from `codepot-openapi` and `codepotg`.