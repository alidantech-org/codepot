---
title: codepotx workflow
description: Evaluate the official JavaScript rewrite using typed authoring, Handlebars packs, CodepotFile.yml, and the codepotx runtime.
order: 42
---

# `codepotx` workflow

This guide describes the official JavaScript rewrite currently developed inside the monorepo.

## 1. Prepare the workspace

```bash
corepack enable
pnpm install
pnpm --filter codepotx check
pnpm --filter codepotx-cli check
```

## 2. Create `codepotx.config.ts`

```ts
import {
  defineCodepotConfig,
  defineVersionContract,
  z,
} from 'codepotx';

const v1 = defineVersionContract({
  info: { title: 'Example', version: '1.0.0' },
});

const schemas = v1.defineSchemas({
  User: {
    id: z.string().uuid(),
    email: z.string().email(),
  },
});

const users = v1.defineResource({
  name: 'users',
  route: '/users',
});

users.defineRoutes().routes((route) => ({
  listUsers: route.get('/').response(schemas.ref.User.array()),
}));

export default defineCodepotConfig({ contracts: [v1] });
```

## 3. Create a Handlebars pack

```text
templates/typescript/
├── paths.yaml
├── _partials/
└── {model}/[model.name.kebab].ts.hbs
```

Example `paths.yaml`:

```yaml
name: typescript-models
version: 1.0.0

folders:
  model:
    select: schemas.models
    as: model
    mode: each
    parts:
      - src
      - models
```

Example template:

```handlebars
export interface {{model.name.pascal}} {
{{#each model.fields}}
  {{name.camel}}: {{lang.type}};
{{/each}}
}
```

## 4. Create `CodepotFile.yml`

```yaml
allow: true

tasks:
  sdk:
    authoring: ./codepotx.config.ts
    templates: ./templates/typescript
    output: ./src/generated
    clean: [models]
    transactional: true
```

## 5. Inspect before generating

```bash
codepotx validate
codepotx variables sdk
codepotx plan sdk --json
codepotx generate sdk --dry-run
```

## 6. Generate

```bash
codepotx generate sdk
```

The runtime plans and renders before mutation, applies managed writes, updates the task manifest, runs approved commands, and returns structured diagnostics and reports.

## 7. Embed the runtime

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

The same runtime call can sit behind a CLI, web page, editor command, MCP tool, or internal service.
