---
title: Getting started
description: Create an authored contract, template pack, and consumer generation task.
order: 2
---

# Getting started

## 1. Install the workspace packages

```bash
pnpm add -D codepotx codepotx-cli
```

`codepotx` owns its supported Zod runtime. Consumers do not install a separate Zod peer dependency.

## 2. Author contracts

Create `codepotx.config.ts`:

```ts
import { defineCodepotConfig, defineVersionContract, z } from 'codepotx';

const version = defineVersionContract({
  info: {
    title: 'Example API',
    version: '1.0.0',
  },
});

const properties = version.defineProperties('shared', {
  id: z.string().uuid(),
  email: z.string().email(),
});

version.defineSchemas({
  User: {
    id: properties.ref.id,
    email: properties.ref.email,
  },
});

export default defineCodepotConfig({ contracts: [version] });
```

## 3. Create a template pack

```text
templates/
├── paths.yaml
└── {model}/[model.name.snake].ts.hbs
```

```yaml
name: typescript-models
folders:
  model:
    select: schemas.models
    as: model
    mode: each
    parts: [src, models]
```

```handlebars
{{#each model.emit.imports}}
// dependency: {{importPath}}
{{/each}}
export interface {{model.name.pascal}} {}
```

## 4. Bind generation to the consumer project

Create `CodepotFile.yml`:

```yaml
allow: true

tasks:
  sdk:
    authoring: ./codepotx.config.ts
    templates: ./templates
    output: ./generated
    clean: [src]
    transactional: true
```

## 5. Inspect and generate

```bash
codepotx validate
codepotx variables sdk
codepotx plan sdk --json
codepotx generate sdk --dry-run
codepotx generate sdk
```

The first successful write creates `.codepot/manifests/sdk.json`. Future runs use it to classify unchanged files and safely remove only stale files still matching their last generated digest.
